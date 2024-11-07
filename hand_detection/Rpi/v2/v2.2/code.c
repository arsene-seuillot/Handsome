#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

void execute_script(const char *script, int read_pipe[], int write_pipe[]) {
    close(read_pipe[1]);   // Ferme l'écriture dans le pipe de lecture
    close(write_pipe[0]);  // Ferme la lecture dans le pipe d'écriture

    // Redirige le stdin et stdout vers les pipes
    dup2(read_pipe[0], STDIN_FILENO);
    dup2(write_pipe[1], STDOUT_FILENO);

    execlp("python3", "python3", script, NULL);
    perror("Erreur dans execlp");
    exit(1);
}



int main() {
    int pipe1[2];  // Pipe pour script2 -> script1
    int pipe2[2];  // Pipe pour script1 -> script2
    // int pipe3[2];  // Pipe pour script2 -> C

    pipe(pipe1);
    pipe(pipe2);
    // pipe(pipe3);

    pid_t pid1 = fork();
    if (pid1 == 0) {
      //close(pipe1[1]);   // Ferme l'écriture dans le pipe de lecture
      //close(pipe2[0]);  // Ferme la lecture dans le pipe d'écriture

      // Redirige le stdin et stdout vers les pipes
      dup2(pipe1[0], STDIN_FILENO);
      dup2(pipe2[1], STDOUT_FILENO);

      
      execlp("python3", "python3", "hand_rpi.py", NULL);
      perror("Erreur dans execlp");
      exit(1);  
    
    }

    pid_t pid2 = fork();
    if (pid2 == 0) {
        
      //close(pipe1[1]);   // Ferme l'écriture dans le pipe de lecture
      //close(pipe2[0]);  // Ferme la lecture dans le pipe d'écriture

      // Redirige le stdin et stdout vers les pipes
      dup2(pipe2[0], STDIN_FILENO);
      dup2(pipe1[1], STDOUT_FILENO);

      execlp("python3", "python3", "moteur_superviseur.py", NULL);
      perror("Erreur dans execlp");
      exit(1);  

    }

    // close(pipe1[0]);  
    // close(pipe3[1]);  

    wait(NULL);
    wait(NULL);

    return 0;
}
