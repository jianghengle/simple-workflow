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
        <span>Create a New Self Hosted Org</span>
      </h1>

      <div class="notification is-info is-light">
        The new org's data will be hosted in your provided AWS account. As you will have full control over your new org data, this is the most secure way to create or onboard a new org on the platform.
      </div>

      <div class="tabs">
        <ul>
          <li :class="{'is-active': step == 1}"><a @click="step = 1">Step 1: AWS Account</a></li>
          <li :class="{'is-active': step == 2}"><a @click="step = 2">Step 2: Org Id</a></li>
          <li :class="{'is-active': step == 3}"><a @click="step = 3">Step 3: IAM Role</a></li>
          <li :class="{'is-active': step == 4}"><a @click="step = 4">Step 4: Create Org</a></li>
        </ul>
      </div>

      <div v-if="step == 1" class="content">
        <p>An AWS account is required to onboard your org on the myworkflowhub.com platform, so that all your org's workflows data will be resided in your AWS account and you have fully control on them. The cost of your data hosing will be very minimum or almostly zero.</p>
        <p>If you already have an AWS account, you can skip this step and use that account in the following steps. Or you can create AWS account by following <a target="_blank" href="https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/">the AWS instruction here</a>.</p>
        
        <div class="mt-6">
          <button class="button" @click="step=2">Next</button>
        </div>
      </div>

      <div v-if="step == 2">
        <div class="content">
          <p>This step is to set the org id and the AWS region for your org.</p>
          <p>First, you want to determine your org id:
            <ul>
              <li>It needs to be all lowercase with alphabet and digital charactors only.</li>
              <li>It should be simple and easy to remember or somewhat indicating your org name.</li>
              <li>It should be unique or has not been used in the platform, which you can check below.</li>
              <li>It will also be used as the prefix of the DyanmoDB tables and S3 bucket name, so make sure there is <em>NO</em> other DyanmoDB tables in the AWS region or S3 bucket with that prefix. (You do not need to worry about it if you are using a new AWS account created in the first step.)</li>
            </ul>
          </p>

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

          <br />

          <p>
            Secondly, you want to determine the AWS region for your org:
            <ul>
              <li>AWS has several data centers or regions.</li>
              <li>You org's data will be resided in the AWS region you select from the 4 US regions below.</li>
            </ul>
          </p>

          <div class="field">
            <label class="label">AWS Region</label>
            <div class="control">
              <div class="select">
                <select v-model="awsRegion">
                  <option>us-east-1</option>
                  <option>us-east-2</option>
                  <option>us-west-1</option>
                  <option>us-west-2</option>
                </select>
              </div>
            </div>
          </div>

          <br />

          <p>
            Optionally, you can sign in your <a href="https://aws.amazon.com/console/" target="_blank">AWS console</a> to verify your AWS account does not have DyanmoDB tables or S3 buckets with your org id as prefix:
            <ol>
              <li>After signing in AWS console, click the region on top right corner, and then choose the region you just selected above.<img src="images/region.png" /></li>
              <li>Then, type <em>DynamoDB</em> in the search bar and then click the <em>DynamoDB</em> entry to get into the DyanmoDB dashboard.<img src="images/dynamo1.png" /></li>
              <li>Next, click <em>Tables</em> on the sidebar to show all the tables, where you want to verify there should be no tables with your org id as prefix.
                  Please note that the platform will create several tables here, where you can also find all your workflow raw data. <img src="images/dynamo2.png" /></li>
              <li>Then, type <em>S3</em> in the search bar and then click the <em>S3</em> entry to get into the S3 dashboard.<img src="images/s31.png" /></li>
              <li>Here you can see all the S3 buckets you have, and you want to make sure there is no buckets with your org id as prefix.
                  Please also note that the platform will create a new bucket here, which will contain all the files uploaded through the platform.<img src="images/s32.png" /></li>
            </ol>
          </p>

          <p>You are good to go to the next step.</p>

        </div>

        <div class="buttons mt-6">
          <button class="button" @click="step=1">Previous</button>
          <button class="button" @click="step=3">Next</button>
        </div>
      </div>

      <div v-if="step == 3">
        <div class="content">
          <p>This step is to set up the IAM role to be assumed by the platform to set up the DynamoDB tables and S3 bucket in your AWS account.</p>
          <p>Some setups are based on the org id and AWS region defined in the previous step:</p>
          <div class="field">
            <label class="label">Org Id</label>
            <div class="control">
              <input class="input my-disbaled-field" type="text" v-model="orgId" disabled readonly>
            </div>
            <p class="help is-danger" v-if="orgIdError">{{orgIdError}}</p>
          </div>
          <div class="field">
            <label class="label">AWS Region</label>
            <div class="control">
              <input class="input my-disbaled-field" type="text" v-model="awsRegion" disabled readonly>
            </div>
          </div>
          <br />

          <p>
            First, you need to create a new policy:
            <ol>
              <li>After signing in AWS console, type <em>iam</em> in the search bar and then click the <em>IAM</em> entry to get into the IAM dashboard.<img src="images/iam.png" /></li>
              <li>Then, click <em>Policies</em> on the sidebar and then click the <em>Create policy</em> button.<img src="images/policy1.png" /></li>
              <li>
                <span>Next, click <em>JSON</em> tab and copy the policy below to replace the existing policy in the editor. 
                  Note that this policy indicates the platform can access the DynamoDB tables and S3 buckets with name prefix of <em>{{orgId}}-</em>. 
                  And later if you do not want to let the platform to access your data, you can simple change the policy or remove the role we will create later.</span>
                <pre>{{policy}}</pre>
                <img src="images/policy2.png" />
              </li>
              <li>Click <em>Next</em>, and then input the policy name like <em>myworkflowhub-policy</em> and click the create button, and then you have the new policy ready.<img src="images/policy3.png" /></li>
            </ol>
          </p>
          <br />

          <p>
            Next, you need to create a new role using the policy you just created:
            <ol>
              <li>Then, click <em>Roles</em> on the sidebar and then click the <em>Create role</em> button.<img src="images/role1.png" /></li>
              <li>
                <span>Next, in the <em>Trusted entity type</em> select <strong><em>AWS account</em></strong>, and then choose <strong><em>Another AWS account</em></strong>, 
                  and input the platform account id <strong><em>932651416286</em></strong>, and then click <em>Next</em>.</span>
                <img src="images/role2.png" />
              </li>
              <li>Then, choose the policy that you just created, and click <em>Next</em>.<img src="images/role3.png" /></li>
              <li>Then, input the role name like <em>myworkflowhub-role</em>, and click <em>Create role</em> button.<img src="images/role4.png" /></li>
              <li>Then, you should be redirected to <em>Roles</em> dashboard, where you click the role you just created.<img src="images/role5.png" /></li>
              <li>Now, the role is ready and you need to copy the ARN of the role, and paste it below.<img src="images/role6.png" /></li>
            </ol>
          </p>

          <div class="field">
            <label class="label">IAM Role</label>
            <div class="control">
              <input class="input" type="text" v-model="iamRole" >
            </div>
          </div>

          <p>You have set up the the IAM role and good to go to the final step.</p>
          
        </div>
        <div class="buttons mt-6">
          <button class="button" @click="step=2">Previous</button>
          <button class="button" @click="step=4">Next</button>
        </div>
      </div>

      <div v-if="step == 4">
        <div class="content">
          <p>You have set up all things, and now you fill in the org name and click the <em>Create Org</em> button below to create the org:</p>
          <div class="field">
            <label class="label">Org Id</label>
            <div class="control">
              <input class="input my-disbaled-field" type="text" v-model="orgId" disabled readonly>
            </div>
            <p class="help is-danger" v-if="orgIdError">{{orgIdError}}</p>
          </div>
          <div class="field">
            <label class="label">AWS Region</label>
            <div class="control">
              <input class="input my-disbaled-field" type="text" v-model="awsRegion" disabled readonly>
            </div>
          </div>
          <div class="field">
            <label class="label">IAM Role</label>
            <div class="control">
              <input class="input my-disbaled-field" type="text" v-model="iamRole" disabled readonly>
            </div>
            <p class="help is-danger" v-if="!iamRole">IAM role cannot be empty!</p>
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

        </div>
        



        <div class="buttons mt-6">
          <button class="button" @click="step=3">Previous</button>
        </div>
      </div>

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
  name: 'NewSelfHostedOrg',
  data () {
    return {
      error: '',
      success: false,
      waiting: false,
      step: 1,
      orgId: '',
      orgIdAvailbility: null,
      awsRegion: 'us-west-2',
      iamRole: '',
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
      return (this.orgId && !this.orgIdError) && this.awsRegion && this.iamRole && this.orgName
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
        awsRegion: this.awsRegion,
        iamRole: this.iamRole,
        orgName: this.orgName
      }
      this.$http.post(this.server + '/org/create-org/', message).then(resp => {
        this.success = true
        this.$store.commit('user/addOrgId', this.orgId)
        this.creating = false
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
