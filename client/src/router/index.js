import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/user/edit',
    name: 'UserEdit',
    component: () => import('../views/UserEdit.vue')
  },
  {
    path: '/user/request-to-join-org',
    name: 'RequestToJoinOrg',
    component: () => import('../views/RequestToJoinOrg.vue')
  },
  {
    path: '/user/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue')
  },
  {
    path: '/user/change-password/:email/:key/:mode',
    name: 'ChangePassword',
    component: () => import('../views/ChangePassword.vue')
  },
  {
    path: '/org/:orgId/workflow-configs',
    name: 'WorkflowConfigs',
    component: () => import('../views/WorkflowConfigs.vue')
  },
  {
    path: '/org/:orgId/org-config',
    name: 'OrgConfig',
    component: () => import('../views/OrgConfig.vue')
  },
  {
    path: '/org/:orgId/org-users',
    name: 'OrgUsers',
    component: () => import('../views/OrgUsers.vue')
  },
  {
    path: '/org/:orgId/new-workflow-config/:copyFrom',
    name: 'NewWorkflowConfig',
    component: () => import('../views/NewWorkflowConfig.vue')
  },
  {
    path: '/org/:orgId/workflow-config/:configId',
    name: 'WorkflowConfig',
    component: () => import('../views/WorkflowConfig.vue')
  },
  {
    path: '/org/:orgId/workflow-folder/:configId/:folderId',
    name: 'WorkflowFolder',
    component: () => import('../views/WorkflowFolder.vue')
  },
  {
    path: '/org/:orgId/new-workflow/:configId/:folderId/:copyFrom',
    name: 'NewWorkflow',
    component: () => import('../views/NewWorkflow.vue')
  },
  {
    path: '/org/:orgId/workflow/:configId/:workflowId',
    name: 'Workflow',
    component: () => import('../views/Workflow.vue')
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
