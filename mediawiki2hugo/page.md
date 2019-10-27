---
title: "{{ title }}"
date: 2019-10-19T16:33:41+11:00
draft: false
resources:
{%- if tags %}
tags:
{%- for tag in tags %}
- {{ tag }}{%- endfor %}{% endif %}
{%- if aliases %}
aliases:
{%- for alias in aliases %}
- {{ alias }}{%- endfor %}{% endif %}
---
{{ text }}
