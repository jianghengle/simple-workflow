<template>
  <div v-if="localModel" class="mt-5">
    <div class="field">
      <a class="button is-pulled-right" @click="openNewTransitionModal">
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
        <span>Add Transition</span>
      </a>
      <label class="label">Transitions</label>
    </div>

    <table class="table is-fullwidth is-hoverable transitions-table">
      <thead>
        <tr>
          <th>To State</th>
          <th>Button Label</th>
          <!--<th>Actor</th>-->
        </tr>
      </thead>
      <tbody>
        <tr class="is-clickable" v-for="(t, i) in localModel" :key="stateName + '-t-t-' + i" @click="openTransitionModal(i)">
          <td>{{t.toState}}</td>
          <td>
            {{t.actionLabel}}
          </td>
          <!--<td>
            <div v-for="(g, i) in t.actor.groups" :key="stateName + '-t-t-p-g-' + i">
              <span class="tag" >{{g}}</span>&nbsp;
            </div>
            <div v-for="(g, i) in t.actor.others" :key="stateName + '-t-t-p-o-' + i">
              <span class="tag" >{{g}}</span>&nbsp;
            </div>
          </td>-->
        </tr>
      </tbody>
    </table>
    
    <new-transition-modal :opened="newTransitionModal.opened" :fields="fields" :stateName="stateName" :stateNames="stateNames"
      @new-transition-modal-closed="onNewTransitionModalClosed" @new-transition-modal-saved="onNewTransitionModalSaved" />
    
    <transition-modal :opened="transitionModal.opened" :model="transitionModal.model" :fields="fields" :stateName="stateName" :stateNames="stateNames"
      @transition-modal-closed="onTransitionModalClosed" @transition-modal-saved="onTransitionModalSaved" @transition-modal-removed="onTransitionModalRemoved" />

  </div>
</template>

<script>
import NewTransitionModal from '@/components/modals/NewTransitionModal'
import TransitionModal from '@/components/modals/TransitionModal'

export default {
  name: 'StateTransitions',
  components: {
    NewTransitionModal,
    TransitionModal
  },
  props: ['model', 'fields', 'stateName', 'stateNames'],
  data () {
    return {
      localModel: null,
      newTransitionModal: {
        opened: false,
      },
      transitionModal: {
        opened: false,
        model: null,
        index: null,
      },
    }
  },
  watch: {
    model: function (val) {
      if (val) {
        this.setLocalModel()
      }
    },
    localModel: {
      handler (val) {
        this.$emit('model-changed', ['transitions', this.localModel])
      },
      deep: true,
    }
  },
  methods: {
    setLocalModel () {
      if (this.model) {
        var modelJson = JSON.stringify(this.model)
        var localModelJson = JSON.stringify(this.localModel)
        if (modelJson != localModelJson) {
          this.localModel = JSON.parse(modelJson)
        }
      }
    },
    openNewTransitionModal () {
      this.newTransitionModal.opened = true
    },
    onNewTransitionModalClosed () {
      this.newTransitionModal.opened = false
    },
    onNewTransitionModalSaved (val) {
      this.localModel.push(JSON.parse(JSON.stringify(val)))
      this.newTransitionModal.opened = false
    },
    openTransitionModal (index) {
      this.transitionModal.index = index
      this.transitionModal.model = this.localModel[index]
      this.transitionModal.opened = true
    },
    onTransitionModalClosed () {
      this.transitionModal.opened = false
    },
    onTransitionModalSaved (val) {
      this.localModel.splice(this.transitionModal.index, 1, JSON.parse(JSON.stringify(val)))
      this.transitionModal.opened = false
    },
    onTransitionModalRemoved () {
      this.localModel.splice(this.transitionModal.index, 1)
      this.transitionModal.opened = false
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">
.transitions-table {
  margin-top: -15px;
}
</style>
