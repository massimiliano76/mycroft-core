pipeline {
    agent any
    triggers {
        cron('0 * * * *')
    }
    stages {

        // Run the build in the against the dev branch to check for compile errors
        stage('Build Docker Image') {
            when {
                anyOf {
                    branch 'testing/behave'
                    changeRequest target: 'dev'
                }
            }
            steps {
                echo 'Building Docker image'
                sh 'docker build --no-cache -t mycroft-core:latest .'
                echo 'Running Docker image'
                sh 'docker run mycroft-core:latest'
                echo 'Cleaning up Docker containers and images'
                sh 'docker container prune --force'
                sh 'docker image prune --force'
            }
        }
    }
}
