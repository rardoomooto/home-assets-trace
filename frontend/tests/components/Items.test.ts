import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import Items from '@/views/Items.vue'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'
import { useRoomStore } from '@/stores/room'

// Mock vue-router with query parameters
const mockRoute = {
  query: {
    expiring_soon: 'true',
    name: 'Test',
    category_id: '1',
    room_id: '2',
    expired: 'false'
  }
}

vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  })),
  useRoute: vi.fn(() => mockRoute)
}))

describe('Items.vue URL filter integration', () => {
  let wrapper: any
  let itemStore: any
  let categoryStore: any

  beforeEach(() => {
    wrapper = mount(Items, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: false
          })
        ],
        stubs: {
          'router-link': {
            template: '<a><slot /></a>',
            props: ['to']
          }
        }
      }
    })
    itemStore = useItemStore()
    categoryStore = useCategoryStore()
    
    // Set up category store with test data
    categoryStore.categories = [
      { id: 1, name: 'Category 1' },
      { id: 2, name: 'Category 2' }
    ]
  })

  it('initializes filterExpiringSoon from URL query parameter', async () => {
    // Wait for onMounted to complete
    await wrapper.vm.$nextTick()
    
    // Check that the checkbox for expiring soon is checked
    const checkbox = wrapper.find('input[type="checkbox"]')
    expect(checkbox.element.checked).toBe(true)
  })

  it('initializes searchName from URL query parameter', async () => {
    await wrapper.vm.$nextTick()
    
    const searchInput = wrapper.find('input[placeholder="输入物品名称"]')
    expect(searchInput.element.value).toBe('Test')
  })

  it('initializes selectedCategory from URL query parameter', async () => {
    await wrapper.vm.$nextTick()
    
    // Wait for category store to be populated
    await new Promise(resolve => setTimeout(resolve, 0))
    
    const categorySelect = wrapper.findAll('select')[0]
    expect(categorySelect.element.value).toBe('1')
  })

  it('calls fetchItems with correct parameters when URL has expiring_soon', async () => {
    await wrapper.vm.$nextTick()
    
    // Check that fetchItems was called with expiring_soon parameter
    expect(itemStore.fetchItems).toHaveBeenCalled()
    const callArgs = itemStore.fetchItems.mock.calls[0][0]
    expect(callArgs.expiring_soon).toBe(true)
  })

  it('calls fetchItems with correct parameters when URL has name filter', async () => {
    await wrapper.vm.$nextTick()
    
    const callArgs = itemStore.fetchItems.mock.calls[0][0]
    expect(callArgs.name).toBe('Test')
  })

  it('calls fetchItems with correct parameters when URL has category_id', async () => {
    await wrapper.vm.$nextTick()
    
    const callArgs = itemStore.fetchItems.mock.calls[0][0]
    expect(callArgs.category_id).toBe(1)
  })
})

describe('Items.vue without URL parameters', () => {
  let wrapper: any
  let itemStore: any

  beforeEach(() => {
    // Reset mock route to have no query parameters
    mockRoute.query = {}
    
    wrapper = mount(Items, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: false
          })
        ],
        stubs: {
          'router-link': {
            template: '<a><slot /></a>',
            props: ['to']
          }
        }
      }
    })
    itemStore = useItemStore()
  })

  it('does not initialize filters when URL has no query parameters', async () => {
    await wrapper.vm.$nextTick()
    
    const checkbox = wrapper.find('input[type="checkbox"]')
    expect(checkbox.element.checked).toBe(false)
    
    const searchInput = wrapper.find('input[placeholder="输入物品名称"]')
    expect(searchInput.element.value).toBe('')
  })

  it('calls fetchItems without filter parameters when URL has no query', async () => {
    await wrapper.vm.$nextTick()
    
    expect(itemStore.fetchItems).toHaveBeenCalled()
    const callArgs = itemStore.fetchItems.mock.calls[0][0]
    expect(callArgs.expiring_soon).toBeUndefined()
    expect(callArgs.name).toBeUndefined()
    expect(callArgs.category_id).toBeUndefined()
  })
})

describe('Items.vue room filter functionality', () => {
  let wrapper: any
  let itemStore: any
  let roomStore: any

  beforeEach(() => {
    mockRoute.query = {}
    
    wrapper = mount(Items, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: false
          })
        ],
        stubs: {
          'router-link': {
            template: '<a><slot /></a>',
            props: ['to']
          }
        }
      }
    })
    itemStore = useItemStore()
    roomStore = useRoomStore()
    
    // Set up room store with test data
    roomStore.rooms = [
      { id: 1, name: 'Room 1' },
      { id: 2, name: 'Room 2' },
      { id: 3, name: 'Room 3' }
    ]
  })

  it('resets currentPage to 1 when room filter changes', async () => {
    await wrapper.vm.$nextTick()
    
    // Simulate user selecting a room
    const roomSelect = wrapper.findAll('select')[1] // Second select is room select
    await roomSelect.setValue(2)
    
    // Check that currentPage was reset to 1
    expect(wrapper.vm.currentPage).toBe(1)
  })

  it('calls fetchItems with room_id when room is selected', async () => {
    await wrapper.vm.$nextTick()
    
    // Clear previous calls
    itemStore.fetchItems.mockClear()
    
    // Simulate user selecting a room
    const roomSelect = wrapper.findAll('select')[1]
    await roomSelect.setValue(2)
    
    // Check that fetchItems was called with room_id
    expect(itemStore.fetchItems).toHaveBeenCalled()
    const callArgs = itemStore.fetchItems.mock.calls[0][0]
    expect(callArgs.room_id).toBe(2)
  })

  it('calls fetchItems without room_id when "全部" is selected', async () => {
    await wrapper.vm.$nextTick()
    
    // Clear previous calls
    itemStore.fetchItems.mockClear()
    
    // First select a room
    const roomSelect = wrapper.findAll('select')[1]
    await roomSelect.setValue(2)
    
    // Then select "全部"
    await roomSelect.setValue(null)
    
    // Check that fetchItems was called without room_id
    expect(itemStore.fetchItems).toHaveBeenCalled()
    const callArgs = itemStore.fetchItems.mock.calls[itemStore.fetchItems.mock.calls.length - 1][0]
    expect(callArgs.room_id).toBeUndefined()
  })

  it('resets currentPage when other filters change', async () => {
    await wrapper.vm.$nextTick()
    
    // Simulate user changing page
    wrapper.vm.currentPage = 3
    await wrapper.vm.$nextTick()
    
    // Clear previous calls
    itemStore.fetchItems.mockClear()
    
    // Simulate user selecting a category
    const categorySelect = wrapper.findAll('select')[0]
    await categorySelect.setValue(1)
    
    // Check that currentPage was reset to 1
    expect(wrapper.vm.currentPage).toBe(1)
  })

  it('maintains currentPage when only page changes', async () => {
    await wrapper.vm.$nextTick()
    
    // Clear previous calls
    itemStore.fetchItems.mockClear()
    
    // Simulate user changing page
    wrapper.vm.currentPage = 2
    await wrapper.vm.$nextTick()
    
    // Check that currentPage is still 2
    expect(wrapper.vm.currentPage).toBe(2)
    
    // Check that fetchItems was called with skip for page 2
    expect(itemStore.fetchItems).toHaveBeenCalled()
    const callArgs = itemStore.fetchItems.mock.calls[0][0]
    expect(callArgs.skip).toBe(20) // (2-1) * 20
  })
})