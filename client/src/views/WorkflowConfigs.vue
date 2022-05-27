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
              <router-link class="button" :to="'/org/' + org.id + '/new-workflow-config/new'">
                <span class="icon">
                  <i class="fas fa-plus"></i>
                </span>
                <span>New Workflow Config</span>
              </router-link>
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
            <div class="box is-clickable" v-for="(w, i) in availableConfigs" :key="'w-c-' + i" @click="viewWorkflows(w)">
              <article class="media">
                <div class="media-content">
                  <div class="content">
                    <p>
                      <strong>{{w.name}}</strong> &nbsp;
                      <span class="icon is-small has-text-link" v-if="isAdmin" @click.stop="editWorkflowConfig(w)">
                        <i class="fas fa-edit" aria-hidden="true"></i>
                      </span>
                      <br>
                      <span>
                        {{w.description}}
                      </span>
                    </p>
                  </div>
                  
                </div>
              </article>
            </div>
            <div v-if="!availableConfigs.length">
              <article class="message is-info">
                <div class="message-body">
                  No workflow config available yet. You can create one if you are able to.
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
      this.$router.push('/org/' + this.orgId + '/workflow-folder/' + w.id + '/' +w.id)
    },
    editWorkflowConfig (wc) {
      this.$router.push('/org/' + this.orgId + '/workflow-config/' + wc.id)
    },
  },
  mounted () {
  }
}
</script>

<style scoped>

</style>