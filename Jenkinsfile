pipeline {
    agent any
    options {
        // Running builds concurrently could cause a race condition with
        // building the Docker image.
        disableConcurrentBuilds()
    }
    environment {
        // Some branches have a "/" in their name (e.g. feature/new-and-cool)
        // Some commands, such as those tha deal with directories, don't
        // play nice with this naming convention.  Define an alias for the
        // branch name that can be used in these scenarios.
        BRANCH_ALIAS = sh(
            script: 'echo $BRANCH_NAME | sed -e "s#/#_#g"',
            returnStdout: true
        ).trim()
    }
    stages {
        // Run the build in the against the dev branch to check for compile errors
        stage('Run Integration Tests') {
            when {
                anyOf {
                    branch 'testing/behave'
                    branch 'dev'
                    branch 'master'
                    changeRequest target: 'dev'
                }
            }
            steps {
                echo 'Building Test Docker Image'
//                 sh 'docker build --no-cache --target voigt_kampff -t mycroft-core:${BRANCH_ALIAS} .'
                echo 'Running Tests'
                timeout(time: 60, unit: 'MINUTES')
                {
                    sh 'docker run \
                        -v "$HOME/voigtmycroft:/root/.mycroft" \
                        --device /dev/snd \
                        -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
                        -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
                        -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
                        mycroft-core:${BRANCH_ALIAS}'
                }
            }
            post {
                always {
                    echo 'Report Test Results'
                    sh 'mv $HOME/voigtmycroft/allure-result allure-result'
                    script {
                        allure([
                            includeProperties: false,
                            jdk: '',
                            properties: [],
                            reportBuildPolicy: 'ALWAYS',
                            results: [[path: 'allure-result']]
                        ])
                    }
                    unarchive mapping:['allure-report.zip': 'allure-report.zip']
//                     sh(
//                         label: 'Package Report',
//                         script: 'tar -czf ${BRANCH_NO_SLASH}.tar.gz allure-report'
//                     )
                    sh (
                        label: 'Copy Report to Web Server',
                        script: 'scp allure-report.zip root@157.245.127.234:~/${BRANCH_ALIAS}.zip'
                    )
                    sh 'ssh root@157.245.127.234 "mkdir -p /var/www/voigt-kampff/${BRANCH_ALIAS}"'
                    sh (
                        label: 'Copy Report to Web Server',
                        script: 'ssh root@157.245.127.234 "unzip -o ~/${BRANCH_ALIAS}.zip /var/www/voigt-kampff/${BRANCH_ALIAS}"'
                    )
                    echo 'Report Published'
                }
            }
        }
    }
    post {
        cleanup {
            sh(
                label: 'Docker container and image cleanup',
                script: '''
                    docker container prune --force
                    docker image prune --force
                '''.stripIndent()
            )
        }
    }
}
