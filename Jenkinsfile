pipeline {
    agent any
    options {
        // Running builds concurrently could cause a race condition with
        // building the Docker image.
        disableConcurrentBuilds()
    }
    triggers {
        cron('0 * * * *')
    }
    stages {
        // Run the build in the against the dev branch to check for compile errors
        stage('Build Docker Image') {
            steps {
                sh 'docker build --no-cache -t mycroft-core:latest .'
            }
        }
        stage('Run Integration Tests') {
            when {
                anyOf {
                    allOf {
                        branch 'testing/behave'
                        triggeredBy 'TimerTrigger'
                    }
                    changeRequest target: 'dev'
                }
            }
            steps {
                sh 'docker run mycroft-core:latest'
            }
        }
        stage('Clean Up Docker') {
            steps {
                sh 'docker container prune --force'
                sh 'docker image prune --force'
            }
        }
    }
}
