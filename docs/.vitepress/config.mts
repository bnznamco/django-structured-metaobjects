import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Django Structured Metaobjects',
  description: 'User-defined typed JSON objects for Django, powered by django-structured-json-field',
  base: '/django-structured-metaobjects/',
  lang: 'en-US',

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/quickstart' },
      { text: 'API', link: '/api/models' },
      { text: 'Changelog', link: '/changelog' },
    ],

    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Quick Start', link: '/guide/quickstart' },
          { text: 'Field Kinds', link: '/guide/field-kinds' },
        ],
      },
      {
        text: 'API Reference',
        items: [
          { text: 'Models', link: '/api/models' },
          { text: 'Serializers', link: '/api/serializers' },
          { text: 'Views', link: '/api/views' },
        ],
      },
      {
        text: 'Other',
        items: [
          { text: 'Changelog', link: '/changelog' },
          { text: 'Contributing', link: '/contributing' },
        ],
      },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/bnznamco/django-structured-metaobjects' },
    ],
  },
})
