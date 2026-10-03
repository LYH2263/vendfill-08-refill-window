<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api, errMsg } from '../api'

interface Loc {
  id: number
  code: string
  name: string
  address: string
  window_start_min: number | null
  window_end_min: number | null
  window_open: boolean
}

const rows = ref<Loc[]>([])
const drafts = reactive<Record<number, { start: string; end: string }>>({})
const msgs = reactive<Record<number, { text: string; ok: boolean }>>({})

function fmtMin(m: number | null): string {
  if (m === null || m === undefined) return ''
  return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`
}
function windowText(r: Loc): string {
  if (r.window_start_min === null && r.window_end_min === null) return '不限时段'
  return `${fmtMin(r.window_start_min)} – ${fmtMin(r.window_end_min)}`
}

async function load() {
  rows.value = await api('/locations')
  for (const r of rows.value) {
    drafts[r.id] = {
      start: r.window_start_min === null ? '' : String(r.window_start_min),
      end: r.window_end_min === null ? '' : String(r.window_end_min),
    }
  }
}

function toMin(v: string): number | null {
  const t = (v ?? '').trim()
  return t === '' ? null : Number(t)
}

async function save(r: Loc) {
  delete msgs[r.id]
  try {
    await api(`/locations/${r.id}`, {
      method: 'PUT',
      body: JSON.stringify({
        window_start_min: toMin(drafts[r.id].start),
        window_end_min: toMin(drafts[r.id].end),
      }),
    })
    // 以刚保存的窗界为准，当场重新拉取判定结果
    await load()
    msgs[r.id] = { text: '已保存', ok: true }
  } catch (e) {
    msgs[r.id] = { text: errMsg(e), ok: false }
  }
}

onMounted(load)
</script>
<template>
  <h1>点位 / 机位</h1>
  <p class="sub">补货时段窗：一天内分钟数，半开区间 [开始, 结束)；两格皆空 = 不限时段</p>
  <div class="vf-site-rail" style="flex-direction:row;flex-wrap:wrap;border:none;background:transparent;padding:0;gap:0.5rem;margin-bottom:1rem">
    <div v-for="r in rows" :key="r.id" class="vf-site-btn" style="min-width:140px">
      <strong style="display:block;color:var(--vf-led)">{{ r.code }}</strong>
      <span style="font-size:0.7rem">{{ r.name }}</span>
    </div>
  </div>
  <div class="card">
    <table>
      <thead>
        <tr><th>编码</th><th>名称</th><th>地址</th><th>时段窗</th><th>开始(分)</th><th>结束(分)</th><th>当前状态</th><th></th></tr>
      </thead>
      <tbody>
        <template v-for="r in rows" :key="r.id">
          <tr>
            <td>{{ r.code }}</td>
            <td>{{ r.name }}</td>
            <td>{{ r.address }}</td>
            <td>{{ windowText(r) }}</td>
            <td>
              <input v-model="drafts[r.id].start" class="min-input" type="number" min="0" max="1440" step="1" placeholder="空" />
            </td>
            <td>
              <input v-model="drafts[r.id].end" class="min-input" type="number" min="0" max="1440" step="1" placeholder="空" />
            </td>
            <td>
              <span class="badge" :class="r.window_open ? 'badge-ok' : 'badge-bad'">
                {{ r.window_open ? '当前可补货' : '不在补货时段' }}
              </span>
            </td>
            <td><button class="btn" @click="save(r)">保存</button></td>
          </tr>
          <tr v-if="msgs[r.id]">
            <td colspan="8">
              <span :style="{ color: msgs[r.id].ok ? 'var(--vf-led)' : 'var(--vf-red)', fontSize: '0.75rem' }">
                {{ msgs[r.id].text }}
              </span>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
<style scoped>
.min-input {
  width: 5.5rem;
  background: #0a0e14;
  color: var(--vf-text);
  border: 1px solid #3a4656;
  border-radius: 3px;
  padding: 0.3rem 0.4rem;
  font: inherit;
  font-size: 0.78rem;
}
.min-input:focus { outline: none; border-color: var(--vf-led); }
</style>
