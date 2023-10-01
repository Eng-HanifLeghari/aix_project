node {
  stage('SCM') {
    checkout scm
  }
  stage('SonarQube Analysis') {
    def scannerHome = tool 'SONAR_SERVER';
    withSonarQubeEnv() {
      sh "${scannerHome}/bin/sonar-scanner"
    }
  }
}
/*pipeline {
  agent  { label 'Local_Test' }
  stages {
    stage ('Clean docker Image'){
      steps {
        sh 'docker rmi -f smart_backend_web'
        sh 'docker system prune -a --volumes'
        sh 'docker-compose rm'
            }
          }
    stage ('Start container'){
      steps {
        sh 'docker-compose up -d'
        sh 'docker-compose ps'
            }
          }
        }
}*/
