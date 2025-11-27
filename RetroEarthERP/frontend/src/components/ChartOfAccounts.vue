<template>
  <div class="chart-of-accounts-container">
    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Account Tree View -->
      <div class="account-tree-panel">
        <div class="panel-header">
          <h2>{{ currentCategoryName }}</h2>
          <button @click="showCreateForm = true" class="btn-create">
            <span>➕</span> New Account
          </button>
        </div>

        <div class="tree-view" v-if="accountTree.length > 0">
          <AccountTreeNode
            v-for="account in accountTree"
            :key="account.id"
            :account="account"
            :level="0"
            @select="selectAccount"
          />
        </div>
        <div v-else class="empty-state">
          <p>No accounts found in this category</p>
        </div>
      </div>

      <!-- Account Details Panel (Bottom) -->
      <div class="details-panel" v-if="selectedAccount">
        <div class="panel-header">
          <h3>Account Properties</h3>
          <div class="actions">
            <button @click="editAccount" class="btn-edit">✏️ Edit</button>
            <button @click="deleteAccount" class="btn-delete">🗑️ Delete</button>
          </div>
        </div>

        <div class="details-grid">
          <div class="detail-row">
            <label>Code:</label>
            <span class="value">{{ selectedAccount.code }}</span>
          </div>
          <div class="detail-row">
            <label>Name (TH):</label>
            <span class="value">{{ selectedAccount.name_th }}</span>
          </div>
          <div class="detail-row">
            <label>Name (EN):</label>
            <span class="value">{{ selectedAccount.name_en || '-' }}</span>
          </div>
          <div class="detail-row">
            <label>Level:</label>
            <span class="value">{{ selectedAccount.account_level }}</span>
          </div>
          <div class="detail-row">
            <label>Type:</label>
            <span class="value">{{ selectedAccount.is_postable ? 'Active Account' : 'Title Account' }}</span>
          </div>
          <div class="detail-row">
            <label>Normal Balance:</label>
            <span class="value">{{ selectedAccount.normal_balance }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Sidebar: Category Drawers (SAP B1 Style) -->
    <div class="drawer-sidebar">
      <div
        v-for="category in categories"
        :key="category.code"
        class="drawer-tab"
        :class="{ active: currentCategory === category.code }"
        @click="selectCategory(category.code)"
      >
        <div class="drawer-label">
          <span class="drawer-icon">{{ category.icon }}</span>
          <span class="drawer-text">{{ category.name }}</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Form Modal -->
    <div v-if="showCreateForm" class="modal-overlay" @click.self="showCreateForm = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editMode ? 'Edit Account' : 'Create New Account' }}</h3>
          <button @click="showCreateForm = false" class="btn-close">✖</button>
        </div>

        <form @submit.prevent="saveAccount" class="account-form">
          <div class="form-group">
            <label>Account Code *</label>
            <input v-model="formData.code" type="text" required :disabled="editMode" />
          </div>

          <div class="form-group">
            <label>Name (Thai) *</label>
            <input v-model="formData.name_th" type="text" required />
          </div>

          <div class="form-group">
            <label>Name (English)</label>
            <input v-model="formData.name_en" type="text" />
          </div>

          <div class="form-group">
            <label>Account Level *</label>
            <select v-model.number="formData.account_level" required>
              <option :value="1">Level 1 (Category)</option>
              <option :value="2">Level 2 (Group)</option>
              <option :value="3">Level 3 (Sub-Group)</option>
              <option :value="4">Level 4 (Account)</option>
              <option :value="5">Level 5 (Detail)</option>
            </select>
          </div>

          <div class="form-group">
            <label>
              <input type="checkbox" v-model="formData.is_postable" />
              Postable (Active Account)
            </label>
          </div>

          <div class="form-group">
            <label>Normal Balance *</label>
            <select v-model="formData.normal_balance" required>
              <option value="DEBIT">Debit</option>
              <option value="CREDIT">Credit</option>
            </select>
          </div>

          <div class="form-actions">
            <button type="button" @click="showCreateForm = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-save">{{ editMode ? 'Update' : 'Create' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import AccountTreeNode from './AccountTreeNode.vue';

const API_BASE = 'http://localhost:8000';

// State
const currentCategory = ref('ASSET');
const accountTree = ref([]);
const selectedAccount = ref(null);
const showCreateForm = ref(false);
const editMode = ref(false);

const formData = ref({
  code: '',
  name_th: '',
  name_en: '',
  account_type: 'ASSET',
  account_level: 1,
  is_postable: true,
  normal_balance: 'DEBIT',
  parent_id: null
});

// Categories (SAP B1 Style Drawers)
const categories = [
  { code: 'ASSET', name: 'Assets', icon: '💰', name_th: 'สินทรัพย์' },
  { code: 'LIABILITY', name: 'Liabilities', icon: '📋', name_th: 'หนี้สิน' },
  { code: 'EQUITY', name: 'Equity', icon: '🏛️', name_th: 'ทุน' },
  { code: 'REVENUE', name: 'Revenue', icon: '📈', name_th: 'รายได้' },
  { code: 'EXPENSE', name: 'Expenses', icon: '📉', name_th: 'ค่าใช้จ่าย' }
];

const currentCategoryName = computed(() => {
  const cat = categories.find(c => c.code === currentCategory.value);
  return cat ? `${cat.name_th} (${cat.name})` : '';
});

// Methods
const selectCategory = (categoryCode) => {
  currentCategory.value = categoryCode;
  selectedAccount.value = null;
  loadAccountTree();
};

const loadAccountTree = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE}/api/chart-of-accounts/tree`, {
      params: { category: currentCategory.value },
      headers: { Authorization: `Bearer ${token}` }
    });
    accountTree.value = response.data;
  } catch (error) {
    console.error('Failed to load account tree:', error);
    alert('Failed to load accounts');
  }
};

const selectAccount = (account) => {
  selectedAccount.value = account;
};

const editAccount = () => {
  formData.value = { ...selectedAccount.value };
  editMode.value = true;
  showCreateForm.value = true;
};

const deleteAccount = async () => {
  if (!confirm('Are you sure you want to deactivate this account?')) return;

  try {
    const token = localStorage.getItem('token');
    await axios.delete(`${API_BASE}/api/chart-of-accounts/${selectedAccount.value.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    alert('Account deactivated successfully');
    selectedAccount.value = null;
    loadAccountTree();
  } catch (error) {
    console.error('Failed to delete account:', error);
    alert(error.response?.data?.detail || 'Failed to delete account');
  }
};

const saveAccount = async () => {
  try {
    const token = localStorage.getItem('token');
    formData.value.account_type = currentCategory.value;

    if (editMode.value) {
      await axios.put(
        `${API_BASE}/api/chart-of-accounts/${selectedAccount.value.id}`,
        formData.value,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Account updated successfully');
    } else {
      await axios.post(`${API_BASE}/api/chart-of-accounts/`, formData.value, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Account created successfully');
    }

    showCreateForm.value = false;
    editMode.value = false;
    resetForm();
    loadAccountTree();
  } catch (error) {
    console.error('Failed to save account:', error);
    alert(error.response?.data?.detail || 'Failed to save account');
  }
};

const resetForm = () => {
  formData.value = {
    code: '',
    name_th: '',
    name_en: '',
    account_type: currentCategory.value,
    account_level: 1,
    is_postable: true,
    normal_balance: 'DEBIT',
    parent_id: null
  };
};

onMounted(() => {
  loadAccountTree();
});
</script>

<style scoped>
.chart-of-accounts-container {
  display: flex;
  height: 100vh;
  background: #c0c0c0;
  font-family: 'MS Sans Serif', Arial, sans-serif;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
  gap: 10px;
}

.account-tree-panel {
  flex: 1;
  background: #f5f5dc; /* Beige */
  border: 3px solid;
  border-color: #ffffff #808080 #808080 #ffffff;
  padding: 10px;
  overflow-y: auto;
}

.details-panel {
  height: 200px;
  background: #f5f5dc;
  border: 3px solid;
  border-color: #ffffff #808080 #808080 #ffffff;
  padding: 10px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #8b4513; /* Brown */
}

.panel-header h2,
.panel-header h3 {
  margin: 0;
  color: #654321;
  font-size: 18px;
}

.tree-view {
  font-size: 14px;
}

.details-grid {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 10px;
}

.detail-row {
  display: contents;
}

.detail-row label {
  font-weight: bold;
  color: #654321;
}

.detail-row .value {
  color: #333;
}

/* Drawer Sidebar (SAP B1 Style) */
.drawer-sidebar {
  width: 120px;
  background: #8b7355; /* Dark brown */
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 5px;
}

.drawer-tab {
  background: #a0826d; /* Lighter brown - inactive */
  border: 2px solid #654321;
  border-left: none;
  padding: 15px 10px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 0 8px 8px 0;
}

.drawer-tab:hover {
  background: #b8956a;
}

.drawer-tab.active {
  background: #f5f5dc; /* Beige - matches main area */
  border-left: 3px solid #8b4513;
  transform: translateX(-3px);
}

.drawer-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.drawer-icon {
  font-size: 24px;
}

.drawer-text {
  font-size: 11px;
  font-weight: bold;
  color: #333;
  text-align: center;
}

/* Buttons */
.btn-create,
.btn-edit,
.btn-delete,
.btn-save,
.btn-cancel {
  padding: 5px 15px;
  border: 2px solid;
  border-color: #ffffff #000000 #000000 #ffffff;
  background: #c0c0c0;
  cursor: pointer;
  font-family: inherit;
  font-size: 12px;
}

.btn-create:active,
.btn-edit:active,
.btn-delete:active,
.btn-save:active {
  border-color: #000000 #ffffff #ffffff #000000;
}

.btn-save {
  background: #008000;
  color: white;
}

.btn-delete {
  background: #c00000;
  color: white;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #c0c0c0;
  border: 3px solid;
  border-color: #ffffff #000000 #000000 #ffffff;
  width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  background: #000080;
  color: white;
  padding: 5px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close {
  background: #c0c0c0;
  border: 2px solid;
  border-color: #ffffff #000000 #000000 #ffffff;
  padding: 2px 8px;
  cursor: pointer;
}

.account-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group select {
  width: 100%;
  padding: 5px;
  border: 2px solid;
  border-color: #808080 #ffffff #ffffff #808080;
  background: white;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>
