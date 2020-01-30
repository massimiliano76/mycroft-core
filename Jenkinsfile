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
            when {
                anyOf {
                    branch 'testing/behave'
                    branch 'dev'
                    branch 'master'
                    triggeredBy 'TimerTrigger'
                    changeRequest target: 'dev'
                }
            }
            steps {
                sh 'cp test/integrationtests/voigt_kampff/Dockerfile ./'
                sh 'docker build --no-cache -t mycroft-core:latest .'
            }
        }
        stage('Run Integration Tests') {
            when {
                anyOf {
                    branch 'testing/behave'
                    branch 'dev'
                    branch 'master'
                    triggeredBy 'TimerTrigger'
                    changeRequest target: 'dev'
                }
            }
            steps {
                sh 'docker run \
                    -v "$HOME/voigtmycroft:/root/.mycroft" \
                    --device /dev/snd \
                    -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
                    -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
                    -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
                    mycroft-core:latest'
            }
        }
        
    }
    post {
        always('Clean Up Docker') {
            echo 'Cleaning up docker containers and images'
            sh 'docker container prune --force'
            sh 'docker image prune --force'
        }
    }
}
