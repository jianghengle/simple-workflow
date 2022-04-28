<template>
  <div v-if="localModel" class="mt-6">
    <div class="field mb-4">
      <button class="button is-pulled-right" @click="addNewState">
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
        <span>New State</span>
      </button>
      <label class="label">States</label>
    </div>

    <div class="tabs is-boxed">
      <ul>
        <li v-for="(state, i) in localModel" :key="'state-tab-'+i" :class="{'is-active': i == currentStateIndex}">
          <a @click="currentStateIndex = i">
            <span>{{state.name}}</span>&nbsp;
            <button class="delete is-small" v-if="i != 0" @click.stop="removeState(i)"></button>
          </a>
        </li>
      </ul>
    </div>


    <custom-state :model="currentState" :index="currentStateIndex" :fields="fields" :stateNames="stateNames" @model-changed="onStateChanged" />

  </div>
</template>

<script>
import NewCustomFieldModal from '@/components/modals/NewCustomFieldModal'
import CustomState from '@/components/workflow/CustomState'

export default {
  name: 'CustomStates',
  components: {
    NewCustomFieldModal,
    CustomState
  },
  props: ['model', 'fields'],
  data () {
    return {
      localModel: [],
      newCustomStateModal: {
        opened: false
      },
      currentStateIndex: 0,
    }
  },
  computed: {
    currentState () {
      return this.localModel[this.currentStateIndex]
    },
    stateNames () {
      return this.localModel.map(s => s.name)
    },
  },
  watch: {
    model: function (val) {
      this.setLocalModel()
    },
    localModel: {
      handler (val) {
        this.$emit('model-changed', ['states', this.localModel])
      },
      deep: true,
    },
  },
  methods: {
    setLocalModel () {
      var modelJson = JSON.stringify(this.model)
      var localModelJson = JSON.stringify(this.localModel)
      if (modelJson != localModelJson) {
        this.localModel = JSON.parse(modelJson)
      }
    },
    addNewState () {
      this.localModel.push({
        name: 'New',
        permissions: {
          view: {
            groups: ['All'],
            others: []
          },
          save: {
            groups: ['All'],
            others: []
          },
          delete: {
            groups: [],
            others: []
          }
        },
        transitions: [],
      })
      this.currentStateIndex = this.localModel.length - 1
    },
    onStateChanged (val) {
      this.localModel.splice(val[0], 1, val[1])
    },
    removeState (index) {
      var confirm = {
        title: 'Remove State',
        message: 'Are you sure to remove this state?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.removeStateConfirmed,
          args: [index]
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    removeStateConfirmed (index) {
      this.localModel.splice(index, 1)
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">

</style>
