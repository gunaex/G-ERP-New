<template>
  <div class="tree-node" :style="{ paddingLeft: `${level * 20}px` }">
    <div
      class="node-content"
      :class="{ 
        'title-account': !account.is_postable,
        'active-account': account.is_postable
      }"
      @click="$emit('select', account)"
    >
      <span v-if="account.children && account.children.length > 0" class="expand-icon" @click.stop="toggleExpand">
        {{ expanded ? '▼' : '▶' }}
      </span>
      <span v-else class="expand-icon">📄</span>
      
      <span class="account-code">{{ account.code }}</span>
      <span class="account-name">{{ account.name_th }}</span>
      <span v-if="!account.is_postable" class="title-badge">Title</span>
    </div>

    <div v-if="expanded && account.children && account.children.length > 0" class="children">
      <AccountTreeNode
        v-for="child in account.children"
        :key="child.id"
        :account="child"
        :level="level + 1"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  account: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
});

defineEmits(['select']);

const expanded = ref(props.level < 2); // Auto-expand first 2 levels

const toggleExpand = () => {
  expanded.value = !expanded.value;
};
</script>

<style scoped>
.tree-node {
  margin: 2px 0;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  cursor: pointer;
  border-radius: 3px;
  transition: background 0.2s;
}

.node-content:hover {
  background: #e6d8c3;
}

.expand-icon {
  width: 16px;
  font-size: 12px;
  cursor: pointer;
  user-select: none;
}

.account-code {
  font-weight: bold;
  color: #654321;
  min-width: 60px;
}

.account-name {
  flex: 1;
  color: #333;
}

.title-account {
  font-weight: bold;
}

.title-account .account-name {
  color: #8b4513;
  font-family: serif;
}

.active-account .account-name {
  font-family: sans-serif;
}

.title-badge {
  background: #8b4513;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: bold;
}

.children {
  margin-left: 0;
}
</style>
