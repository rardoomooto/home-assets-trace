import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import Home from '@/views/Home.vue'
import { useItemStore } from '@/stores/item'
import { useCategoryStore } from '@/stores/category'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  })),
  useRoute: vi.fn(() => ({
    query: {}
  }))
}))

describe('Home.vue', () => {
  let wrapper: any
  let itemStore: any
  let categoryStore: any

  beforeEach(() => {
    wrapper = mount(Home, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: false
          })
        ],
        stubs: {
          'router-link': {
            template: '<a :href="computedHref"><slot /></a>',
            props: ['to'],
            computed: {
              computedHref() {
                if (typeof this.to === 'string') {
                  return this.to
                }
                if (typeof this.to === 'object' && this.to.path) {
                  let href = this.to.path
                  if (this.to.query) {
                    const queryParams = Object.entries(this.to.query)
                      .map(([key, value]) => `${key}=${value}`)
                      .join('&')
                    if (queryParams) {
                      href += '?' + queryParams
                    }
                  }
                  return href
                }
                return '/'
              }
            }
          }
        }
      }
    })
    itemStore = useItemStore()
    categoryStore = useCategoryStore()
  })

  it('renders three stat cards', () => {
    const cards = wrapper.findAll('.bg-white.overflow-hidden.shadow.rounded-lg')
    expect(cards.length).toBe(3)
  })

  it('has clickable stat cards with correct links', async () => {
    // Check that there are three router-link components
    const routerLinks = wrapper.findAll('a')
    expect(routerLinks.length).toBeGreaterThanOrEqual(3)
    
    // Check that one of them has href="/items"
    const itemsLink = routerLinks.find((link: any) => link.attributes('href') === '/items')
    expect(itemsLink.exists()).toBe(true)
    
    // Check that one of them has href="/categories"
    const categoriesLink = routerLinks.find((link: any) => link.attributes('href') === '/categories')
    expect(categoriesLink.exists()).toBe(true)
    
    // Check that one of them has href="/items?expiring_soon=true"
    const expiringSoonLink = routerLinks.find((link: any) => {
      const href = link.attributes('href')
      return href && href.includes('/items') && href.includes('expiring_soon=true')
    })
    expect(expiringSoonLink.exists()).toBe(true)
  })

  it('displays total items count', async () => {
    itemStore.total = 42
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('42')
  })

  it('displays total categories count', async () => {
    categoryStore.categories = [{ id: 1, name: 'Category 1' }, { id: 2, name: 'Category 2' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('2')
  })

  it('displays expiring soon count', async () => {
    // Set up items with expiry dates
    const today = new Date()
    const tenDaysLater = new Date(today.getTime() + 10 * 24 * 60 * 60 * 1000)
    const fortyDaysLater = new Date(today.getTime() + 40 * 24 * 60 * 60 * 1000)
    
    itemStore.items = [
      { id: 1, name: 'Item 1', expiry_date: tenDaysLater.toISOString().split('T')[0] },
      { id: 2, name: 'Item 2', expiry_date: fortyDaysLater.toISOString().split('T')[0] },
      { id: 3, name: 'Item 3', expiry_date: null }
    ]
    
    await wrapper.vm.$nextTick()
    
    // Should show 1 expiring soon item (within 30 days)
    expect(wrapper.text()).toContain('1')
  })

  it('has header with title and add button in flex container', () => {
    // Check that there's a flex container with justify-between
    const headerContainer = wrapper.find('.flex.items-center.justify-between')
    expect(headerContainer.exists()).toBe(true)
    
    // Check that the title is in the header
    const title = headerContainer.find('h1')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('仪表盘')
    
    // Check that the add button is in the header
    const addButton = headerContainer.find('a[href="/items/new"]')
    expect(addButton.exists()).toBe(true)
    expect(addButton.text()).toContain('添加物品')
  })

  it('does not have duplicate add buttons', () => {
    // Check that there's only one add button
    const addButtons = wrapper.findAll('a[href="/items/new"]')
    expect(addButtons.length).toBe(1)
  })
})