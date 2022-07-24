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
      <a class="button back-button" @click="$router.go(-1)">
        <span class="icon back-icon">
          <i class="fas fa-angle-left"></i>
        </span>
      </a>

      <h1 class="title is-size-4 my-title mt-4">
        <span>Create a New Platform Hosted Org</span>
      </h1>
      <div class="notification is-info is-light">
        The new org's data will be hosted in your the platform's AWS account, and you can access the data through the platform.
      </div>

      <div class="field">
        <label class="label">Org Id</label>
        <div class="field has-addons mb-0">
          
          <div class="control">
            <input class="input" type="text" placeholder="Input your org id" v-model="orgId">
          </div>
          <div class="control">
            <a class="button is-info" @click="checkAvailbility" :class="{'is-loading': waiting}">
              Check Availbility
            </a>
          </div>
        </div>
        <p class="help is-danger" v-if="orgIdError">{{orgIdError}}</p>
        <p class="help is-success" v-if="orgIdAvailbility != null && orgIdAvailbility">Yeah you can use this org id!</p>
        <p class="help is-danger" v-if="orgIdAvailbility != null && !orgIdAvailbility">This org id has been used!</p>
      </div>

      <div class="field">
        <label class="label">Org Name</label>
        <div class="control">
          <input class="input" type="text" v-model="orgName">
        </div>
        <p class="help is-info">The org name show in the header. You can change it anytime after creation.</p>
      </div>

      <div class="field is-grouped mt-5 mb-1">
        <div class="control">
          <button class="button is-link" :class="{'is-loading': creating, 'my-disabled-button': !canCreate}" :disabled="!canCreate" @click="createOrg">Create Org</button>
        </div>
      </div>
      <p class="help is-info">Please be patient as the creation process may take up to one minutes.</p>

      <div v-if="error" class="notification is-danger is-light mt-4">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>

      <div v-if="success" class="notification is-success is-light mt-4">
        The new org has been created successfully. You can now click <router-link :to="'/org/' + orgId + '/workflow-configs'">here</router-link> to go to your new org.
      </div>

    </div>

    
  </div>
</template>

<script>

var policy = `{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "dynamodb:*"
            ],
            "Resource": [
                "arn:aws:dynamodb:$2:932651416286:table/$1-*"
            ],
            "Effect": "Allow"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$1-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::$1-*"
            ]
        }
    ]
}
`;

export default {
  name: 'NewPlatformHostedOrg',
  data () {
    return {
      error: '',
      success: false,
      waiting: false,
      orgId: '',
      orgIdAvailbility: null,
      orgName: '',
      creating: false,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    orgIdError () {
      if (!this.orgId) {
        return 'Your org id cannot be empty.'
      }
      var re = /^([a-z\d][a-z\d]*)$/
      if (!re.test(this.orgId)) {
        return 'Your must only contain lowercase alphabet and digital charactors.'
      }
      return ''
    },
    policy () {
      return policy.replaceAll('$1', this.orgId).replaceAll('$2', this.awsRegion)
    },
    canCreate () {
      return (this.orgId && !this.orgIdError) && this.orgName
    },
  },
  methods: {
    checkAvailbility () {
      if (this.waiting || this.orgIdError) {
        return
      }
      this.waiting = true
      this.orgIdAvailbility = null
      this.$http.post(this.server + '/org/check-org-id/', {orgId: this.orgId}).then(resp => {
        this.orgIdAvailbility = true
        this.waiting = false
      }, err => {
        this.orgIdAvailbility = false
        this.waiting = false
      })
    },
    createOrg () {
      if (this.creating || !this.canCreate) {
        return
      }
      this.creating = true
      this.success = ''
      this.error = ''
      var message = {
        orgId: this.orgId,
        orgName: this.orgName,
        awsRegion: 'us-west-2'
      }
      this.$http.post(this.server + '/org/create-role-for-platform-hosted-org/', message).then(resp => {
        message.iamRole = resp.body.awsRole
        this.$http.post(this.server + '/org/create-org/', message).then(resp => {
          this.success = true
          this.$store.commit('user/addOrgId', this.orgId)
          this.creating = false
        }, err => {
          this.error = 'Something went wrong when creating the new org. You might need to start it over or contact the author jianghengle@gmail.com'
          this.creating = false
        })
      }, err => {
        this.error = 'Something went wrong when creating the new org. You might need to start it over or contact the author jianghengle@gmail.com'
        this.creating = false
      })
    }
  },
}
</script>

<style scoped lang="scss">
 
</style>
