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
                echo 'Building Docker Image'
                sh 'docker build --no-cache -t mycroft-core:latest .'
                sh 'docker run mycroft-core:latest'
                sh 'docker container prune --force'
                sh 'docker image prune --force'
            }
        }
    }
}
