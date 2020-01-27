pipeline {
    agent any

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
                sh 'echo ' + env.BRANCH_NAME
            }
        }
    }
}
