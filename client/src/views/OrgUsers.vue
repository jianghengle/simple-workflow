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
      <div v-if="!orgUsers">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <div v-if="!isAdmin">
          <div class="message-body">
            You are not allowed to view this page
          </div>
        </div>
        <div v-else>
          <div class="my-title-section">

            <router-link class="button back-button" :to="'/org/' + org.id + '/workflow-configs'">
              <span class="icon back-icon">
                <i class="fas fa-angle-left"></i>
              </span>
            </router-link>

            <h1 class="title is-size-4 my-title">
              <span>Org Users</span>
            </h1>
          </div>

          <div class="mt-3">
            <div class="buttons is-pulled-right">
              <a class="button" @click="openNewOrgUserModal">
                <span class="icon">
                  <i class="fas fa-user-plus"></i>
                </span>
                <span>New User</span>
              </a>
            </div>
            <div class="buttons">
              <div class="control has-icons-left">
                <div class="select">
                  <select v-model="seletedGroup">
                    <option>All</option>
                    <option v-for="(g, i) in groupOptions" :key="'filter-group-option-' + i">{{g}}</option>
                  </select>
                </div>
                <div class="icon is-small is-left">
                  <i class="fas fa-filter"></i>
                </div>
              </div>
            </div>
          </div>

          <div v-if="error" class="notification is-danger is-light">
            <button class="delete" @click="error=''"></button>
            {{error}}
          </div>

          <div>
            <table class="table is-fullwidth is-striped is-hoverable">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Groups</th>
                  <th class="has-text-centered">Activated</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(user, i) in showingOrgUsers" :key="'org-user-' + i" class="is-clickable" @click="openUserModal(user)">
                  <td>{{i + 1}}</td>
                  <td>{{user.email}}</td>
                  <td>{{user.role}}</td>
                  <td>
                    <span class="tag is-medium ml-1" v-for="(group, j) in user.groups" :key="'org-user-' + i + '-group-' + j">
                      {{group}}
                    </span>
                  </td>
                  <td class="has-text-centered">
                    <span v-if="user.activated">Yes</span>
                    <span v-else>
                      <span v-if="sent[user.email]" class="has-text-success">Invitation Sent</span>
                      <span v-else>
                        <a class="button" :class="{'is-loading': sending[user.email]}" @click.stop="sendInvitation(user)">Send Invitation</a>
                      </span>
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>

          </div>
        </div>

      </div>
    </div>

    <org-user-modal :opened="orgUserModal.opened" :orgUser="orgUserModal.orgUser" @org-user-modal-closed="onOrgUserModalClosed" />
    <new-org-user-modal :opened="newOrgUserModal.opened" :defaultGroup="seletedGroup" @new-org-user-modal-closed="onNewOrgUserModalClosed" />
    
  </div>
</template>

<script>
import Vue from 'vue'
import OrgUserModal from '@/components/modals/OrgUserModal'
import NewOrgUserModal from '@/components/modals/NewOrgUserModal'

export default {
  name: 'OrgUsers',
  components: {
    OrgUserModal,
    NewOrgUserModal
  },
  data () {
    return {
      error: '',
      waiting: false,
      orgUserModal: {
        opened: false,
        orgUser: null,
      },
      newOrgUserModal: {
        opened: false,
      },
      seletedGroup: 'All',
      sending: {},
      sent: {},
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
    isAdmin () {
      if (!this.orgUser) {
        return false
      }
      return this.orgUser.role == 'Owner' || this.orgUser.role == 'Admin'
    },
    groupOptions () {
      if (!this.orgUsers) {
        return ['All']
      }
      var groups = new Set()
      this.orgUsers.forEach(function(user) {
        if (user.groups) {
          user.groups.forEach(function(g) {
            groups.add(g)
          })
        }
      })
      return Array.from(groups)
    },
    showingOrgUsers () {
      var seletedGroup = this.seletedGroup
      if (seletedGroup == 'All') {
        return this.orgUsers
      }
      return this.orgUsers.filter(function(orgUser) {
        return orgUser.groups.includes(seletedGroup)
      })
    },
  },
  methods: {
    openUserModal (orgUser) {
      this.orgUserModal.orgUser = orgUser
      this.orgUserModal.opened = true
    },
    onOrgUserModalClosed () {
      this.orgUserModal.opened = false
      this.orgUserModal.orgUser = null
    },
    openNewOrgUserModal () {
      this.newOrgUserModal.opened = true
    },
    onNewOrgUserModalClosed () {
      this.newOrgUserModal.opened = false
    },
    sendInvitation (user) {
      if (this.sending[user.email]) {
        return
      }
      this.$set(this.sending, user.email, true)
      this.$http.post(this.server + '/user/send-invite', user).then(resp => {
        this.$set(this.sending, user.email, false)
        this.$set(this.sent, user.email, true)
      }, err => {
        this.$set(this.sending, user.email, false)
        this.error = err
        this.sending = false
      })
    },
  },
}
</script>

<style scoped lang="scss">
  .my-title-section {
    height: 50px;
    
    .back-button {
      float: left;
    }

    .my-title {
      margin-left: 50px;
      position: relative;
      top: 7px;
    }

    .new-user-button {
      position: absolute;
      top: 7px;
      right: 0px;
    }
  }
 
</style>
