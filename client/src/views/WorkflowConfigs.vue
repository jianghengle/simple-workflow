<template>
  <div class="container mt-5 px-2">
    <div v-if="!token">
      <article class="message is-danger">
        <div class="message-body">
          You have not signed in yet. Please go back to <a href="/">home page</a> to sign in first.
        </div>
      </article>
    </div>
    <div v-else>
      <div v-if="!orgUser">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

        <div v-if="!availableConfigs">
          <span class="icon is-medium is-size-4">
            <i class="fas fa-spinner fa-pulse"></i>
          </span>
        </div>
        <div v-else>
          <div class="mb-6">
            <div class="buttons is-pulled-right" v-if="isAdmin && org">

              <div class="dropdown my-dropdown mr-2" :class="{'is-active': dropdownOpened}">
                <div class="dropdown-trigger">
                  <button class="button mb-0" aria-haspopup="true" aria-controls="dropdown-menu" @click="toggleDropdown">
                    <span class="icon">
                      <i class="fas fa-plus"></i>
                    </span>
                    <span>New Workflow Config</span>
                    <span class="icon is-small">
                      <i class="fas fa-angle-down" aria-hidden="true"></i>
                    </span>
                  </button>
                </div>
                <div class="dropdown-menu" id="dropdown-menu" role="menu">
                  <div class="dropdown-content">
                    <router-link class="dropdown-item" :to="'/org/' + org.id + '/new-workflow-config/new'">
                      From Blank Template
                    </router-link>
                    <hr class="dropdown-divider">
                    <div class="dropdown-item" v-if="!templates.length">
                      <span class="icon is-small is-size-6">
                        <i class="fas fa-spinner fa-pulse"></i>
                      </span>
                    </div>
                    <router-link class="dropdown-item" v-for="(t, i) in templates" :key="'d-t-'+i" :to="'/org/' + org.id + '/new-workflow-config-from-template/' + t.id">
                      From Template: <strong>{{t.name}}</strong>
                    </router-link>
                  </div>
                </div>
              </div>

              <router-link class="button" :to="'/org/' + org.id + '/org-users'">
                <span class="icon">
                  <i class="fas fa-user-cog"></i>
                </span>
                <span>Users</span>
              </router-link>
              <router-link class="button" :to="'/org/' + org.id + '/org-config'">
                <span class="icon">
                  <i class="fas fa-cog"></i>
                </span>
                <span>Config</span>
              </router-link>
            </div>
            <h1 class="title is-size-4">
              <span v-if="org">{{org.name}}</span>
            </h1>
          </div>

          <div class="pt-2">
            <div class="box" v-for="(w, i) in availableConfigs" :key="'w-c-' + i">
              <article class="media">
                <div class="media-content">
                  <div class="content">
                    <p>
                      <strong>{{w.name}}</strong> &nbsp;
                      <a class="icon is-small has-text-link" v-if="isAdmin" @click="editWorkflowConfig(w)">
                        <i class="fas fa-edit" aria-hidden="true"></i>
                      </a>
                      <br>
                      <span>
                        {{w.description}}
                      </span>
                    </p>
                    <div class="buttons">
                      <button class="button" @click="viewWorkflows(w)">View All</button>
                      <button class="button" @click="createWorkflow(w)">
                        <span v-if="w.creationButton">
                          {{w.creationButton}}
                        </span>
                        <span v-else>
                          New Workflow
                        </span>
                      </button>
                    </div>
                  </div>
                  
                </div>
              </article>
            </div>
            <div v-if="!availableConfigs.length">
              <article class="message is-info">
                <div class="message-body">
                  No workflow config available in the org yet. You can create new workflow config if you are an admin.
                </div>
              </article>
            </div>
          </div>
        </div>

      </div>
    </div>

    
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'WorkflowConfigs',
  data () {
    return {
      error: '',
      waiting: false,
      workflowConfigs: null,
      dropdownOpened: false,
      templates: [],
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    email () {
      return this.$store.state.user.email
    },
    orgId () {
      return this.$route.params.orgId
    },
    org () {
      return this.$store.state.org.org
    },
    orgUsers () {
      return this.$store.state.org.orgUsers
    },
    orgUser () {
      if (!this.email || !this.orgUsers) {
        return null
      }
      var email = this.email
      return this.orgUsers.filter(function(u){
        return u.email == email
      })[0]
    },
    orgWorkflowConfigs () {
      return this.$store.state.org.orgWorkflowConfigs
    },
    isAdmin () {
      if (!this.orgUser) {
        return false
      }
      return this.orgUser.role == 'Owner' || this.orgUser.role == 'Admin'
    },
    availableConfigs () {
      if (!this.orgWorkflowConfigs) {
        return null
      }
      if (this.isAdmin) {
        return this.orgWorkflowConfigs
      }
      if (!this.orgUser) {
        return null
      }
      var configs = []
      for (const c of this.orgWorkflowConfigs) {
        if (c.userGroup == 'All' || this.orgUser.groups.includes(c.userGroup)) {
          configs.push(c)
        }
      }
      return configs
    },
  },
  methods: {
    viewWorkflows (w) {
      this.$router.push('/org/' + this.orgId + '/workflow-folder/' + w.id + '/' + w.id)
    },
    createWorkflow (w) {
      this.$router.push('/org/' + this.orgId + '/new-workflow/' + w.id + '/' + w.id + '/new')
    },
    editWorkflowConfig (wc) {
      this.$router.push('/org/' + this.orgId + '/workflow-config/' + wc.id)
    },
    toggleDropdown () {
      this.dropdownOpened = !this.dropdownOpened
      if (!this.templates.length) {
        this.$http.get(this.server + '/template/get-all-templates/').then(resp => {
          this.templates = resp.body
        }, err => {
          console.log('Failed to get templates')
        })
      }
    },
  },
  mounted () {
  }
}
</script>

<style scoped>
.my-dropdown {
  margin-top: -7px;
}
</style>