#include "../common/common.h"

int main(void)
{
    int sockfd; 
    printf("Client: Enter lines of text, ^D to quit:\n");

    struct my_msgbuf buf; 
    char mtext[200] = { '0' };

    sockfd  = connectSocket();
    if(sockfd < 0)
    {
        perror("CLIENT: Connection Failed to server socket");
        exit(0);
    }

#ifdef AUTO_TEST_MODE
    while (1)
    {
        strcpy(mtext, "abcdefghijklmnopqrstuvwxyz");
#else
        while(fgets(mtext, sizeof(mtext), stdin) != NULL)
#endif
        {
            long len = strlen(mtext);
            long sent = 0;
            /* ditch newline at end, if it exists */
            
            if (mtext[len-1] == '\n') mtext[len-1] = '\0';
#ifndef AUTO_TEST_MODE
            if (len == 1) continue; //It is only a \n no need to transmit.
            len = len-1;
#endif
            //Start Perfomance Monitoring per PID
            startMonitoring(&buf);
          
            sent = sendData (sockfd, mtext, len);
            if(sent < 0)
            {
                perror("Client: Write Failed");
                continue;
            }

            printf("\nClient Sent: %s (Len=%ld bytes)\n", mtext, sent);
            
            len = recv(sockfd, mtext, MAX_BUFFER, 0);
            if(len < 0)
            {
                perror("Client Rx failed  ...continuing");
                continue;
            }

            printf("Read Back from Server %s Len (%ld)\n", mtext, len);
        
            //End Monitoring and begin verification
            verifyPerformance(&buf);
        }
#ifdef AUTO_TEST_MODE
    }
#endif

    close (sockfd);
    return 0;
}

int sendData (int sockfd, char* buf, int len)
{
    int ret =  send(sockfd, buf, len, 0);
    if (ret <= 0)
        perror("Write Failed");
    else 
        printf("\nClient fd %d written %d bytes\n", sockfd, ret);

    return ret;

}


