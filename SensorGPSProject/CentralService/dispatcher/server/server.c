#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <unistd.h>
#include <semaphore.h>
#include <pthread.h>
#include <ctype.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <arpa/inet.h>
#include <sys/ioctl.h>


/*****************
 *
 * GLOBAL DATA 
 *
 * ***************/
sem_t semap;
struct timespec tstart={0,0}, tend={0,0};

struct my_msgbuf 
{
    long msender;
    char mtext[200];
};

/**************************
 *
 * FUNCTION DECLARATIONS 
 *
 *************************/
int setupMessageQueues(int *);
int sendMessage (struct my_msgbuf *, int, long );
int startReceive(struct my_msgbuf *, int );
void initSemaphore();
void takeSemaphore();
void releaseSemaphore();
void sendBack(int sockfd);
void startMonitoring();
void verifyPerformance();
int connectSocket();
pid_t Fork(void);

#define MAX_CLIENTS 1024
#define MAX_BUFFER 2048
/*************************/

    int dbsockfd; 
int main(int argc, char **argv)
{
    int                     listenfd, connfd;
    pid_t                   childpid;
    socklen_t               clilen;
    struct sockaddr_in      cliaddr, servaddr;

    dbsockfd = connectSocket();
    if (dbsockfd < 0)
      perror ("Database socket connection failed");

    listenfd = socket(PF_INET, SOCK_STREAM, 0);
    if (listenfd < 0)
    {
        perror("Socket creation Failed");
        exit(0);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family      = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port        = htons(12345);

    if (bind(listenfd, (struct sockaddr *) &servaddr, sizeof(servaddr)) < 0)
    {
        perror("Bind Failure");
        exit(0);
    }

    if(listen(listenfd, MAX_CLIENTS) < 0)
    {
        perror("Listen Failure");
        exit(0);
    }

    //initSemaphore();
    for ( ; ; )
    {
        //takeSemaphore();
        clilen = sizeof(cliaddr);
  
        connfd = accept(listenfd, (struct sockaddr *)&cliaddr, &clilen);
        if(connfd < 0)
        {
            perror("Accept Failed");
            continue;
        }

        printf("client connected with ip address: %s\n", inet_ntoa(cliaddr.sin_addr));

        /* Create a child process for concurrent access */
        if ((childpid = Fork()) == 0)
        {
            while(1)
            {
                close(listenfd);     /* close listening socket */
                sendBack(connfd);    /* process the request */
            }
            exit(0);
        }
        close(connfd);               /* parent closes connected socket */
        //releaseSemaphore();
    }
}

pid_t Fork(void)
{
    pid_t   pid;

    if ( (pid = fork()) == -1)
        perror("fork error");
    
    return(pid);
}

int sendData (int sockfd, char* buf, int len)
{
    int ret =  send(sockfd, buf, len, 0);
    if (ret <= 0)
        perror("Write Failed");
    else 
        printf("\nwritten %d\n", ret);
    
    return ret;
}


int connectSocket()
{
    int                 sockfd;
    struct sockaddr_in  servaddr;

    sockfd = socket(PF_INET, SOCK_STREAM, 0);
    
    if (sockfd < 0)
    {
        perror("CLIENT: Socket creation Failed");
        exit(0);
    }


    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    inet_pton(AF_INET, "192.168.43.46", &servaddr.sin_addr);
    servaddr.sin_port = htons(8877);

    if (connect(sockfd, (struct sockaddr *) &servaddr, sizeof(servaddr)) < 0) 
    {
        perror("CLIENT: Connection Failed");
        return -1;
    }

    printf("Client Socket Connected port \n");
    return sockfd;
}





void sendBack(int sockfd)
{
    ssize_t     n = 0;
    char        buf[MAX_BUFFER];

again:
    startMonitoring();
    n = recv(sockfd, buf, MAX_BUFFER, 0);
    if (n > 0) 
    {
        buf[n] = '\0';
        printf("Server Connected and Sending echo pid =%d \n", getpid());
        printf("Server Received: %s (Len=%ld bytes) sockfd (%d) \n", buf, n, sockfd);
        //sendData(sockfd, buf, n);
        sendData(sockfd, "OK", 2);
        sendData(dbsockfd, buf, n);
        verifyPerformance();
    }

    if (n < 0 && errno == EINTR)
        goto again;
    else if (n < 0)
        perror("sendBack: read error");
}

/*************************************************************
 *
 * Setup the IPC MSG QUEUE
 *
 * ***********************************************************/
int setupMessageQueues(int *msqid)
{
    key_t key = ftok("./common/key.c", 'b');
    if (key == 0)
    {
        perror("Server: ftok");
        return -1;
    }
    
    *msqid = msgget(key, 0644 | IPC_CREAT);
    if (*msqid == -1)
    {
        perror("Server: msgget");
        return -1;
    }
    
    printf("Server: Key =[%u] msqid=[%d]\n", key, *msqid);
    return 0;
}

/**************************************************************
 *
 * SendMessage buffer to the specfied Msqid.
 *
 * ***********************************************************/
int sendMessage (struct my_msgbuf *buf,int msqid, long len)
{
    printf("Server: SendMessage [%ld]:Buffer to send [%s], len=[%ld], msqid=[%d] \n", 
                    buf->msender, buf->mtext, len, msqid);

    if (msgsnd(msqid, buf, len, 0) == -1)
    {
        perror("Server: msgsnd");
        return -1;
    }
    
    printf("Server : Sent [%ld] bytes\n", len);
    return len;
}

/**************************************************************
 *
 * startReceive to starting to receive from the IPC MSG QUEUE
 *
 * ***********************************************************/
int startReceive(struct my_msgbuf *buf,int msqid)
{
    long recvLen;
    
    //Reset the last read buffer, to avoid corruption
    memset((void*)buf, 0, sizeof(struct my_msgbuf));
    
    printf("Server: Waiting for incoming message\n");
    
    recvLen = msgrcv(msqid, buf, sizeof(struct my_msgbuf), 0, 0);
    if ( recvLen <= 0) 
    {
        perror("Server: msgrcv");
        return -1; 
    }
    
    buf->mtext[recvLen] = '\0';
    printf("Server: StartReceive Sender [%ld], RxLen [%ld], Buffer received =[%s], msqid=[%d] \n", buf->msender,
                    recvLen, buf->mtext, msqid);

    return recvLen;
}

/**************************************************************
 *
 * Initializing the Semaphores to be used during for locking
 *
 * ***********************************************************/
void initSemaphore()
{
    // InitSemaphore
    sem_init(&semap, 0, 1);
    printf("Semaphore requested.\n");
}

/**********************
 *
 * Lock the Semaphore
 *
 * ********************/
void takeSemaphore()
{
    // lock
    sem_wait(&semap);
    printf("Semaphore set.\n");
}

/**********************
 *
 * UnLock the Semaphore
 *
 * ********************/

void releaseSemaphore()
{
    // unlock
    sem_post(&semap);
    printf("Semaphore unlocked.\n");
}

/**************************************************************
 *
 * startMonitoring Performance (starts timers)
 *
 * ***********************************************************/
void startMonitoring()
{
    clock_gettime(CLOCK_MONOTONIC, &tstart);
}

/**************************************************************
 *
 * End Monitoring delta (take timer and do delta)
 *
 * ***********************************************************/
void verifyPerformance()
{
    clock_gettime(CLOCK_MONOTONIC, &tend);
    
    //printf("\n**********************************************************\n");
    printf("(%d),[%.5f]\n",
           getpid(),
	   ((double)tend.tv_sec + 1.0e-9*tend.tv_nsec) - 
           ((double)tstart.tv_sec + 1.0e-9*tstart.tv_nsec));
    printf("***********--  *********************************************\n");
}
