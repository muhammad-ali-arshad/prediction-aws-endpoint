pipeline {
    // This agent must run on the EC2 instance serving public port 5500.
    agent { label 'ec2-docker' }

    options {
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
    }

    triggers {
        githubPush()
    }

    environment {
        IMAGE_TAG = 'latest'
        DOCKER_CONFIG = "${WORKSPACE}/.docker-config"
    }

    stages {
        stage('Validate agent') {
            steps {
                sh '''
                    set -eu
                    docker info >/dev/null
                    docker compose version
                    python3 --version
                '''
            }
        }

        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKERHUB_LOGIN', passwordVariable: 'DOCKERHUB_TOKEN')]) {
                    script {
                        // Derive the image namespace from the saved credential.
                        env.DOCKERHUB_USERNAME = env.DOCKERHUB_LOGIN
                    }
                    sh '''
                        set -eu
                        set +x
                        docker compose config --quiet
                        docker compose build --pull api
                        mkdir -p "$DOCKER_CONFIG"
                        chmod 700 "$DOCKER_CONFIG"
                        printf '%s' "$DOCKERHUB_TOKEN" | docker login --username "$DOCKERHUB_LOGIN" --password-stdin
                        docker compose push api
                        docker logout
                    '''
                }
                // Leave the container running when this stage and job complete.
                sh 'docker compose up -d --no-build --force-recreate --wait --wait-timeout 60 api'
            }
        }

        stage('Verify prediction') {
            steps {
                sh 'python3 scripts/verify_api.py http://127.0.0.1:5500'
            }
        }
    }

    post {
        failure {
            sh 'docker compose ps; docker compose logs --tail=100 api || true'
        }
        always {
            // Delete only this job's temporary Docker authentication directory.
            dir('.docker-config') {
                deleteDir()
            }
        }
    }
}
