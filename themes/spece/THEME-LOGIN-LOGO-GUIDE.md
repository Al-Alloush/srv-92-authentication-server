# Keycloak Login Theme - Adding a Logo Image

## Why We Created `template.ftl`

Keycloak 26 uses the **base** theme's `template.ftl` as the HTML layout for all login pages. This base template does **not** include an `<img>` tag or a `div.kc-logo-text` element for a custom logo. It only renders the realm display name as plain text inside `#kc-header-wrapper`.

The old Keycloak versions (before v20) had a `div.kc-logo-text` element in the header, which allowed themes to use CSS `background-image` to show a logo. In Keycloak 26, that HTML element no longer exists in the base template.

**CSS-only approaches (`::before` pseudo-elements, `background-image`) are unreliable** because:
- The `div.kc-logo-text` element doesn't exist in the rendered HTML
- PatternFly CSS resets can interfere with pseudo-elements
- The `#kc-header-wrapper` has no fixed dimensions, so background images may not display

**The solution**: Override the base `template.ftl` by placing a custom copy in the theme's `login/` folder. Keycloak automatically uses a theme's `template.ftl` if it exists, falling back to the parent theme's version if not. In our custom version, we added an actual `<img>` tag that reliably displays the logo.

---

## Steps to Add a Logo to a New Login Theme

### 1. Create the Theme Folder Structure

```
keycloak/themes/<your-theme-name>/
├── login/
│   ├── template.ftl                    # Custom template (overrides base)
│   ├── theme.properties                # Theme configuration
│   └── resources/
│       ├── css/
│       │   └── login.css               # Custom styles
│       └── img/
│           ├── favicon.ico
│           ├── keycloak-bg.png          # Background image
│           └── your-logo.png           # Your logo image
├── common/
│   └── resources/
│       └── img/
│           └── favicon.ico
├── email/
│   └── theme.properties
└── welcome/
    ├── index.ftl
    ├── theme.properties
    └── resources/
        └── css/
            └── welcome.css
```

### 2. Add Your Logo Image

Place your logo PNG file in:
```
keycloak/themes/<your-theme-name>/login/resources/img/your-logo.png
```

Recommended: PNG format with transparency, square aspect ratio (e.g., 926x926px).

### 3. Create `template.ftl`

Copy the `template.ftl` from an existing theme (e.g., `imeterrecorder/login/template.ftl`) and modify the header section.

The key part is inside `#kc-header-wrapper`. Find this block:

```html
<div id="kc-header-wrapper" class="${properties.kcHeaderWrapperClass!}">
```

And make sure it contains:

```html
<div id="kc-header-wrapper" class="${properties.kcHeaderWrapperClass!}">
    <div id="kc-logo-wrapper">
        <img src="${url.resourcesPath}/img/your-logo.png"
             alt="${realm.displayName!''}"
             id="kc-logo-image" />
    </div>
    ${kcSanitize(msg("loginTitleHtml",(realm.displayNameHtml!'')))?no_esc}
</div>
```

**Important notes:**
- `${url.resourcesPath}` resolves to the theme's `login/resources/` path automatically
- Change `your-logo.png` to your actual logo filename
- The realm display name text is kept below the logo

### 4. Add CSS Styles for the Logo

In `login/resources/css/login.css`, add these rules:

```css
/* Logo wrapper - centers the logo */
#kc-logo-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin: 0 auto 10px;
}

/* Logo image - fixed size, centered */
#kc-logo-image {
    display: block;
    width: 150px;           /* Adjust size as needed */
    height: 150px;          /* Adjust size as needed */
    max-width: 150px;
    max-height: 150px;
    object-fit: contain;    /* Maintains aspect ratio */
    margin: 0 auto;
}

/* Header wrapper - center text below logo */
#kc-header-wrapper {
    font-size: 29px;
    text-transform: uppercase;
    letter-spacing: 3px;
    line-height: 1.2em;
    padding: 62px 10px 20px;
    white-space: normal;
    text-align: center;
}
```

### 5. Configure `theme.properties`

Make sure `login/theme.properties` includes:

```properties
parent=base
import=common/keycloak

styles=css/login.css
stylesCommon=vendor/patternfly-v4/patternfly.min.css vendor/patternfly-v3/css/patternfly.min.css vendor/patternfly-v3/css/patternfly-additions.min.css lib/pficon/pficon.css

meta=viewport==width=device-width,initial-scale=1

kcHtmlClass=login-pf
kcLoginClass=login-pf-page
kcLogoClass=login-pf-brand
kcHeaderClass=login-pf-page-header
kcFormCardClass=card-pf
kcFormHeaderClass=login-pf-header
```

(Copy the full `theme.properties` from an existing theme like `imeterrecorder` for all the other class definitions.)

### 6. Assign the Theme to a Realm

1. Log in to Keycloak Admin Console
2. Select the realm
3. Go to **Realm Settings** → **Themes** tab
4. Set **Login theme** to your new theme name
5. Click **Save**

### 7. Restart Keycloak

```bash
cd /srv/keycloak && docker compose restart keycloak
```

### 8. Clear Browser Cache

Hard-refresh the login page with **Ctrl+Shift+R** (or Cmd+Shift+R on Mac) to bypass cached CSS/images.

---

## Quick Reference: Copy from Existing Theme

The fastest way to create a new theme with a logo is to copy the `imeterrecorder` theme:

```bash
# Copy the entire theme
cp -r /srv/keycloak/themes/imeterrecorder /srv/keycloak/themes/<new-theme-name>

# Replace the logo image
cp /path/to/new-logo.png /srv/keycloak/themes/<new-theme-name>/login/resources/img/

# Update the img filename in template.ftl
# Edit: themes/<new-theme-name>/login/template.ftl
# Change: imeterrecorder-logo.png → new-logo.png

# Update CSS colors/sizes as needed
# Edit: themes/<new-theme-name>/login/resources/css/login.css

# Restart Keycloak
cd /srv/keycloak && docker compose restart keycloak
```

---

## File Reference

| File | Purpose |
|------|---------|
| `template.ftl` | HTML layout for all login pages. Must contain the `<img>` tag for the logo. |
| `theme.properties` | Theme config: parent theme, CSS files, class names. |
| `login.css` | Custom styles for logo size, positioning, colors, backgrounds. |
| `resources/img/` | Logo and background images. |
