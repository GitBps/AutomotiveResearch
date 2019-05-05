#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <arpa/inet.h>

struct my_msgbuf {
    long msender;
    char mtext[200];
};

struct timespec tstart={0,0}, tend={0,0};

int setupMessageQueues(int *, int*);
int sendMessage (struct my_msgbuf *, int, long );
int startReceive(struct my_msgbuf *, int );
void startMonitoring(struct my_msgbuf * );
void verifyPerformance(struct my_msgbuf *);
int connectSocket();
int sendData (int sockfd, char* buf, int len);

#define MAX_CLIENTS 5
#define MAX_BUFFER 2048


/*************************************************************
 *
 * Setup the IPC MSG QUEUE
 *
 * ***********************************************************/
int setupMessageQueues(int *msqid, int *rxqid)
{
    key_t key;
    if ((key = ftok("./common/key.c", 'b')) == -1)
    {
        perror("Server: ftok");
        return -1;
    }
    
    if ((*msqid = msgget(key, 0644 | IPC_CREAT)) == -1)
    {
        perror("Server: msgget");
        return -1;
    }
    
    *rxqid = msgget(getpid(), IPC_CREAT | 0600);
    
    if (*rxqid < 0)
    {
        perror("Error creating the message queue.\n");
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
    //len = sizeof(buf->msender) + len-1;
    printf("Client[%ld]:Buffer to send [%s], len=[%ld], msqid=[%d] \n", buf->msender,
                      buf->mtext, len, msqid);
    
    if (msgsnd(msqid, buf, len, 1) == -1)
    {
        perror("Client: msgsnd");
        return -1;
    }
    
    printf("Client : Sent [%ld] bytes\n", len);
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
    printf("Client: Waiting for incoming message\n");

    recvLen = msgrcv(msqid, buf, sizeof(struct my_msgbuf), 0, 0);
    if ( recvLen < 0)
    {
        perror("Client: msgrcv");
        return -1;
    }

    buf->mtext[recvLen] = '\0';
    printf("Client: Sender [%ld], RxLen [%ld], Buffer received =[%s], msqid=[%d] \n",
                    buf->msender, recvLen, buf->mtext, msqid);
    
    return recvLen;
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
    inet_pton(AF_INET, "localhost", &servaddr.sin_addr);
    servaddr.sin_port = htons(8877);

    if (connect(sockfd, (struct sockaddr *) &servaddr, sizeof(servaddr)) < 0) 
    {
        perror("CLIENT: Connection Failed");
        return -1;
    }

    printf("Client Socket Connected port \n");
    return sockfd;
}

/**************************************************************
 *
 * startMonitoring Performance (starts timers)
 *
 * ***********************************************************/
void startMonitoring(struct my_msgbuf *buf)
{
    clock_gettime(CLOCK_MONOTONIC, &tstart);
}

/**************************************************************
 *
 * End Monitoring delta (take timer and do delta)
 *
 * ***********************************************************/
void verifyPerformance(struct my_msgbuf * buf)
{
    clock_gettime(CLOCK_MONOTONIC, &tend);
    
    printf("\n**********************************************************\n");
    printf("**************** PID -> [%d] ***********************\n", getpid());
    printf("*****************[%.5f] seconds**********************\n",
           ((double)tend.tv_sec + 1.0e-9*tend.tv_nsec) - 
           ((double)tstart.tv_sec + 1.0e-9*tstart.tv_nsec));
    printf("**************** PID -> [%d] ***********************\n", getpid());
    printf("**********************************************************\n");
}
