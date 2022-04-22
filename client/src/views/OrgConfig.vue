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
      <div v-if="!orgUsers || !model">
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
              <span>Org Config</span>
            </h1>
          </div>

          <div v-if="error" class="notification is-danger is-light">
            <button class="delete" @click="error=''"></button>
            {{error}}
          </div>

          <string-field :name="'id'" :label="'Id'" :value="org.id" :readonly="true" />
          <string-field :name="'name'" :label="'Name'" :value="model.name" :placeholder="'Org name'" @value-changed="onValueChanged" />
          <string-field :name="'awsRole'" :label="'AWS Role'" :value="org.awsRole" :readonly="true" />
          <string-field :name="'awsRegion'" :label="'AWS Region'" :value="org.awsRegion" :readonly="true" />
          <string-field :name="'userTable'" :label="'Org Users Table'" :value="org.userTable" :readonly="true" />
          <string-field :name="'workflowConfigTable'" :label="'Org Workflow Configs Table'" :value="org.workflowConfigTable" :readonly="true" />
          <string-field :name="'folderTable'" :label="'Org Workflow Folders Table'" :value="org.folderTable" :readonly="true" />
          <string-field :name="'s3Bucket'" :label="'S3 Bucket'" :value="model.s3Bucket" :placeholder="'S3 Bucket for Files'" @value-changed="onValueChanged" :prefix="org.id + '-'" />


          <div class="field is-grouped mt-6">
            <p class="control">
              <a class="button is-link" :disabled="!modelChanged" :class="{'is-loading': waiting}" @click="save">
                Update
              </a>
            </p>
            <p class="control">
              <a class="button is-light" @click="reset">
                Reset
              </a>
            </p>
          </div>

          <div v-if="modelChanged" class="notification is-warning is-light">
            You have unsaved changes!
          </div>

        </div>

      </div>
    </div>

    
  </div>
</template>

<script>
import Vue from 'vue'
import StringField from '@/components/form/StringField'

export default {
  name: 'OrgConfig',
  components: {
    StringField
  },
  data () {
    return {
      error: '',
      waiting: false,
      model: null,
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
    modelChanged () {
      if (!this.model) {
        return false
      }
      return this.org.name != this.model.name
        || this.org.s3Bucket != this.model.s3Bucket 
    },
  },
  watch: {
    org: function (val) {
      if (val) {
        this.makeOrgModel()
      }
    },
  },
  methods: {
    makeOrgModel () {
      this.model = {
        name: this.org.name,
        s3Bucket: this.org.s3Bucket,
      }
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.model[name] != value) {
        this.model[name] = value
      }
    },
    save () {
      if (this.waiting || !this.modelChanged) {
        return
      }
      this.waiting = true
      this.$http.post(this.server + '/org/update-org/' + this.org.id, this.model).then(resp => {
        var org = resp.body
        Vue.http.headers.common['My-Org-Info'] = btoa(JSON.stringify(org))
        this.$store.commit('org/setOrg', org)
        this.waiting = false
      }, err => {
        this.error = err
        this.waiting = false
      })
    },
    reset () {
      this.makeOrgModel()
    },
  },
  mounted () {
    if (this.org) {
      this.makeOrgModel()
    }
  }
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
  }
 
</style>
