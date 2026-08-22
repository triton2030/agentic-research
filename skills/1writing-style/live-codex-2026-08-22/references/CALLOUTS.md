# Справочник Callouts

## Базовый Callout

```markdown
> [!note]
> Это note callout.

> [!info] Пользовательский Title
> У этого callout есть пользовательский title.

> [!tip] Только Title
```

## Сворачиваемые Callouts

```markdown
> [!faq]- Collapsed by default
> Этот content скрыт, пока его не раскрыть.

> [!faq]+ Expanded by default
> Этот content видим, но его можно свернуть.
```

## Вложенные Callouts

```markdown
> [!question] Внешний callout
> > [!note] Внутренний callout
> > Вложенный content
```

## Поддерживаемые Callout Types

| Type | Aliases | Color / Icon |
|------|---------|-------------|
| `note` | - | Blue, pencil |
| `abstract` | `summary`, `tldr` | Teal, clipboard |
| `info` | - | Blue, info |
| `todo` | - | Blue, checkbox |
| `tip` | `hint`, `important` | Cyan, flame |
| `success` | `check`, `done` | Green, checkmark |
| `question` | `help`, `faq` | Yellow, question mark |
| `warning` | `caution`, `attention` | Orange, warning |
| `failure` | `fail`, `missing` | Red, X |
| `danger` | `error` | Red, zap |
| `bug` | - | Red, bug |
| `example` | - | Purple, list |
| `quote` | `cite` | Gray, quote |

## Пользовательские Callouts (CSS)

```css
.callout[data-callout="custom-type"] {
  --callout-color: 255, 0, 0;
  --callout-icon: lucide-alert-circle;
}
```
