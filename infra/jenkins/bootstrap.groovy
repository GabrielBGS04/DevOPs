import jenkins.model.Jenkins
import hudson.model.BooleanParameterDefinition
import hudson.model.ParametersDefinitionProperty
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition

// Deliberately local-only lab. The launcher binds HTTP to 127.0.0.1.
def jenkins = Jenkins.get()
jenkins.setNumExecutors(1)
jenkins.setSlaveAgentPort(-1)
jenkins.setSecurityRealm(hudson.security.SecurityRealm.NO_AUTHENTICATION)
jenkins.setAuthorizationStrategy(new hudson.security.AuthorizationStrategy.Unsecured())
jenkins.setCrumbIssuer(new hudson.security.csrf.DefaultCrumbIssuer(true))
def root = System.getenv('B1_LAB_ROOT')
['core', 'ia', 'integracoes'].each { component ->
    def name = "b1-${component}"
    def job = jenkins.getItem(name) ?: jenkins.createProject(WorkflowJob.class, name)
    job.setDescription("B1 real native laboratory: tests, artifact build and component deploy. Windows/loopback; no container engine available.")
    job.addProperty(new ParametersDefinitionProperty(new BooleanParameterDefinition('FALHA_CONTROLADA', false, 'Inject a real failing test in disposable workspace; deployment must be skipped.')))
    def pipeline = new File(root, "infra/jenkins/Jenkinsfile.${component}.nativo").getText('UTF-8')
    job.setDefinition(new CpsFlowDefinition(pipeline, true))
    job.save()
}
jenkins.save()
println 'B1_PIPELINES_READY'
