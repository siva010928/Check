pipeline {
    agent any
    stages {
        stage('Initial Setup') {
            steps {
                sh '''
                chmod +x initial-setup.sh
                ./initial-setup.sh
                '''
            }
        }
        stage('Giving Permissions') {
            steps {
                sh '''
                chmod +x permission.sh
                ./permission.sh
                '''
            }
        }
        stage('Setup Python Virtual ENV for dependencies') {
            steps {
                sh '''
                chmod +x env-setup.sh
                ./env-setup.sh
                '''
            }
        }
        stage('Giving staticfiles Permissions') {
            steps {
                sh '''
                chmod +x staticfiles_permission.sh
                ./staticfiles_permission.sh
                '''
            }
        }
        stage('Setup Supervisor Setup') {
            steps {
                sh '''
                chmod +x supervisor.sh
                ./supervisor.sh
                '''
            }
        }
//         stage('Setup NGINX') {
//             steps {
//                 sh '''
//                 chmod +x nginx.sh
//                 ./nginx.sh
//                 '''
//             }
//         }
    }
}
