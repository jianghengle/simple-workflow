<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Exporting workflows</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body pb-6">

        <div class="field">
          <label class="label">Exporting {{workflows.length}} workflow(s) into CSV file</label>
          <div class="control">
            <button class="button is-link" @click="exportWorkflow">Export</button>
          </div>
        </div>

        <div class="field" v-for="(itf, i) in itemsFields" :key="'itf-'+i">
          <div class="control">
            <button class="button is-link" @click="exporItemsField(itf)">
              <span>Export individual subitems from</span>&nbsp;
              <strong><em>{{itf.label}}</em></strong>
            </button>
          </div>
        </div>

      </section>
      <footer class="modal-card-foot">
        <a class="button" @click="close">Close</a>
      </footer>
    </div>
  </div>
</template>

<script>
import { saveAs } from 'file-saver'
import dateFormat from 'dateformat'

export default {
  name: 'export-workflow-modal',
  props: ['opened', 'fields', 'workflows'],
  data () {
    return {
      waiting: false,
      error: '',
    }
  },
  computed: {
    itemsFields () {
      if (!this.fields) {
        return []
      }
      return this.fields.filter(f => f.type == 'items')
    },
  },
  methods: {
    close () {
      this.$emit('export-workflow-modal-closed')
    },
    exportWorkflow () {
      var vm = this
      var header = ['id', 'state']
      header = header.concat(this.fields.map(f => f.name))
      header = header.concat(['createdBy', 'createdAt', 'updatedBy', 'updatedAt'])
      var rows = this.workflows.map(w => {
        return vm.workflowToCsv(w)
      })
      rows.unshift(header.join(','))
      var string = rows.join('\r\n')
      var blob = new Blob([string], {type: 'text/plain;charset=utf-8'})
      saveAs(blob, 'workflows.csv')
    },
    workflowToCsv (workflow) {
      var ss = []
      ss.push(workflow.id)
      ss.push(this.cleanString(workflow.state))
      for (const f of this.fields) {
        if (f.type == 'number') {
          ss.push(String(Number(workflow[f.name])))
        } else if (f.type == 'string' || f.type == 'textarea' || f.type == 'checkbox') {
          ss.push(this.cleanString(String(workflow[f.name])))
        } else {
          ss.push(this.cleanString(JSON.stringify(workflow[f.name])))
        }
      }
      ss.push(String(workflow.createdBy))
      ss.push(dateFormat(new Date(workflow.createdAt), 'isoDateTime'))
      ss.push(String(workflow.updatedBy))
      ss.push(dateFormat(new Date(workflow.updatedAt), 'isoDateTime'))
      return ss.join(',')
    },
    cleanString (s) {
      s = s.replaceAll('"', "'")
      if (s.includes(',') || s.includes('\n') || s.includes('\r')) {
        return '"' + s + '"'
      }
      return s
    },
    exporItemsField (itf) {
      var header = ['id', 'state']
      var fieldNames = []
      for (const f of this.fields) {
        if (f.name == itf.name) {
          for (const sf of f.itemFields) {
            fieldNames.push(f.name + '.' + sf.name)
          }
        } else {
          fieldNames.push(f.name)
        }
      }
      header = header.concat(fieldNames)
      header = header.concat(['createdBy', 'createdAt', 'updatedBy', 'updatedAt'])
      var rows = []
      for (const w of this.workflows) {
        rows = rows.concat(this.workflowWithItemsToCsv(w, itf))
      }
      rows.unshift(header.join(','))
      var string = rows.join('\r\n')
      var blob = new Blob([string], {type: 'text/plain;charset=utf-8'})
      saveAs(blob, 'workflows.csv')
    },
    workflowWithItemsToCsv (workflow, itf) {
      var ss = []
      ss.push(workflow.id)
      ss.push(this.cleanString(workflow.state))
      var index = -1
      for (var i=0;i<this.fields.length;i++) {
        var f = this.fields[i]
        if (f.name == itf.name) {
          index = i
          continue
        }
        if (f.type == 'number') {
          ss.push(String(Number(workflow[f.name])))
        } else if (f.type == 'string' || f.type == 'textarea' || f.type == 'checkbox') {
          ss.push(this.cleanString(String(workflow[f.name])))
        } else {
          ss.push(this.cleanString(JSON.stringify(workflow[f.name])))
        }
      }
      ss.push(String(workflow.createdBy))
      ss.push(dateFormat(new Date(workflow.createdAt), 'isoDateTime'))
      ss.push(String(workflow.updatedBy))
      ss.push(dateFormat(new Date(workflow.updatedAt), 'isoDateTime'))

      var itemsStrings = this.itemsToStrings(workflow[itf.name], itf.itemFields)
      var rows = []
      for (const its of itemsStrings) {
        var row = ss.slice()
        row.splice(index + 2, 0, ...its)
        rows.push(row.join(','))
      }
      return rows
    },
    itemsToStrings (items, fs) {
      if (!items || !items.length) {
        return [fs.map(f => '')]
      }
      var vm = this
      return items.map(item => {
        return fs.map (f => {
          if (f.type == 'number') {
            return String(Number(item[f.name]))
          }
          return vm.cleanString(String(item[f.name]))
        })
      })
    },
  },
}
</script>
