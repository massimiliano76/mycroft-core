pipeline {
    agent any
    options {
        // Running builds concurrently could cause a race condition with
        // building the Docker image.
        disableConcurrentBuilds()
    }
    stages {
        // Run the build in the against the dev branch to check for compile errors
        stage('Run Integration Tests') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                }
            }
            steps {
                sh 'cp test/integrationtests/voight_kampff/Dockerfile.voight_kampff Dockerfile
                sh 'docker build --no-cache --target voigt_kampff -t mycroft-core:latest .'
                timeout(time: 60, unit: 'MINUTES')
                {
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
    }
    post {
        always('Important stuff') {
            echo 'Cleaning up docker containers and images'
            sh 'docker container prune --force'
            sh 'docker image prune --force'
        }
    }
}
