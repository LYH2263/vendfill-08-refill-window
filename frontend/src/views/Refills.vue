<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, errMsg } from '../api'
const data = ref<any>(null)
const error = ref('')
const loading = ref(false)

async function run() {
  loading.value = true
  error.value = ''
  try {
    data.value = await api('/refills/run?location_id=1', { method: 'POST' })
  } catch (e) {
    // 窗外失败：原因原样展示（不在补货时段），页面仍展示最近一次成功单
    error.value = errMsg(e)
    data.value = await api('/refills/latest?location_id=1')
  } finally {
    loading.value = false
  }
}
onMounted(run)
</script>
<template>
  <h1>补货小票</h1>
  <p class="sub">gap = 容量 − 库存 − 在途 · 收据纸样式</p>
  <button class="btn" :disabled="loading" @click="run">生成补货单</button>
  <p v-if="error" class="vf-error">
    {{ error }}<span v-if="data && data.id">，以下为最近一次成功单</span>
  </p>
  <div style="margin-top:1rem" v-if="data && data.id">
    <div class="vf-receipt">
      <h2>*** VendFill 补货单 ***</h2>
      <div class="vf-receipt-line" style="font-weight:700;border-bottom:2px dashed #8a7e64">
        <span>货道 / 商品</span><span>补量</span>
      </div>
      <div class="vf-receipt-line" v-for="l in data.lines" :key="l.lane_id">
        <span>{{ l.slot_no }} {{ l.sku_name }}
          <small>({{ l.status === 'need_fill' ? '待补' : l.status === 'full' ? '满仓' : '超占' }})</small>
        </span>
        <span>{{ l.fill_qty }} / 缺{{ l.gap }}</span>
      </div>
      <p style="text-align:center;margin:1rem 0 0;font-size:0.72rem;color:#6a5e48">谢谢使用 · 请核对后装机</p>
    </div>
  </div>
  <p v-else-if="data" class="muted" style="margin-top:1rem">暂无成功补货单</p>
</template>
<style scoped>
.vf-error {
  color: var(--vf-red);
  font-size: 0.8rem;
  margin: 0.75rem 0 0;
}
</style>
