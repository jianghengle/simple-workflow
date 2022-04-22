<template>
  <div>
    <nav class="navbar is-dark" role="navigation" aria-label="main navigation">
      <div class="container">
        <div class="navbar-brand">
          <router-link class="navbar-item is-size-4 has-text-weight-bold" :to="homeRoute">
            {{brand}}
          </router-link>
          

          <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false"
            :class="{'is-active': menuActive}" @click="menuActive = !menuActive">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </a>
        </div>

        <div id="navbarBasicExample" class="navbar-menu"  :class="{'is-active': menuActive}">
          <div class="navbar-start" v-if="token && availableConfigs">
            <router-link class="navbar-item" v-for="(c, i) in availableConfigs" :key="'config-menu-' + i" :to="'/org/' + orgId + '/workflow-folder/' + c.id + '/' + c.id">
              {{c.name}}
            </router-link >
          </div>

          <div class="navbar-end">
            <div class="navbar-item has-dropdown is-hoverable" v-if="orgIds && orgIds.length > 1">
              <a class="navbar-link">
                <span class="icon">
                  <i class="fas fa-user"></i>
                </span>
              </a>

              <div class="navbar-dropdown">
                <router-link class="navbar-item" v-for="(orgId, i) in orgIds" :key="'h-m-d-' + i" :to="'/org/' + orgId + '/workflow-configs'">
                  {{orgId}}
                </router-link>
              </div>
            </div>
            <router-link class="navbar-item" v-if="!token" :to="'/'">
              <span class="icon">
                <i class="fas fa-sign-in-alt"></i>
              </span>
              <span>Sign in</span>
            </router-link>
            <a class="navbar-item" v-if="token" @click="signout">
              <span class="icon">
                <i class="fas fa-sign-out-alt"></i>
              </span>
              <span>Sign out</span>
            </a>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'Header',
  data () {
    return {
      menuActive: false
    }
  },
  computed: {
    token () {
      return this.$store.state.user.token
    },
    email () {
      return this.$store.state.user.email
    },
    orgIds () {
      return this.$store.state.user.orgIds
    },
    routerPath () {
      return this.$route.path
    },
    server () {
      return this.$store.state.config.server
    },
    orgId () {
      return this.$route.params.orgId
    },
    org () {
      return this.$store.state.org.org
    },
    brand () {
      if (this.org) {
        return this.org.name
      }
      return 'Simple Workflow'
    },
    homeRoute () {
      if (this.org) {
        return '/org/' + this.org.id + '/workflow-configs'
      }
      return '/'
    },
    orgWorkflowConfigs () {
      return this.$store.state.org.orgWorkflowConfigs
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
    isAdmin () {
      if (!this.orgUser) {
        return false
      }
      return this.orgUser.role == 'Owner' || this.orgUser.role == 'Admin'
    },
    availableConfigs () {
      if (this.isAdmin) {
        return this.orgWorkflowConfigs
      }
      if (!this.orgUser) {
        return []
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
  watch: {
    orgId: function (val) {
      if (val) {
        this.$store.commit('org/setOrg', null)
        this.$store.commit('org/setOrgUsers', [])
        this.$store.commit('org/setOrgWorkflowConfigs', null)
        this.setOrg()
      } else {
        this.$store.commit('org/setOrg', null)
        this.$store.commit('org/setOrgUsers', [])
        this.$store.commit('org/setOrgWorkflowConfigs', null)
      }
    },
  },
  methods: {
    signout () {
      var confirm = {
        title: 'Sign Out',
        message: 'Are you sure to sign out?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.signoutConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    signoutConfirmed () {
      delete Vue.http.headers.common['Authorization']
      this.$store.commit('user/reset')
      this.$store.commit('org/setOrg', null)
      this.$store.commit('org/setOrgUsers', [])
      this.$store.commit('org/setOrgWorkflowConfigs', null)
      if (this.routerPath != '/') {
        this.$router.push('/')
      }
    },
    setUser () {
      this.$http.get(this.server + '/user/get-user').then(resp => {
        var user = resp.body
        this.$store.commit('user/setUser', user)
      }, err => {
        console.log('Failed to set user')
      })
    },
    setOrg () {
      this.$http.get(this.server + '/org/get-org/' + this.orgId).then(resp => {
        var org = resp.body
        var orgCopy = JSON.parse(JSON.stringify(org))
        delete orgCopy.name
        Vue.http.headers.common['My-Org-Info'] = btoa(JSON.stringify(orgCopy))
        this.$store.commit('org/setOrg', org)
        this.setOrgUsers()
        this.setOrgWorkflowConfigs()
      }, err => {
        console.log('Failed to set org')
      })
    },
    setOrgUsers () {
      this.$http.get(this.server + '/org/get-org-users').then(resp => {
        var orgUsers = resp.body
        this.$store.commit('org/setOrgUsers', orgUsers)
      }, err => {
        console.log('Failed to set org users')
      })
    },
    setOrgWorkflowConfigs () {
      this.$http.get(this.server + '/org/get-org-workflow-configs').then(resp => {
        var orgWorkflowConfigs = resp.body
        this.$store.commit('org/setOrgWorkflowConfigs', orgWorkflowConfigs)
      }, err => {
        console.log('Failed to set org workflow configs')
      })
    },
  },
  mounted () {
    if (this.token) {
      Vue.http.headers.common['Authorization'] = this.token
      this.setUser()
    }
  }
}
</script>