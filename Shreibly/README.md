# Schreibly · Keycloak login theme

Branded login, registration, password-reset, OTP and error pages — drop-in
theme for any Keycloak ≥ 22 instance.

## Files in this folder

```
keycloak/
├── README.md                          ← you are here
├── theme.properties                   ← Keycloak theme manifest
│
├── login.html                         ← static HTML previews
├── register.html                      ← (open in a browser to inspect)
├── forgot-password.html
├── otp.html
├── error.html
│
├── resources/
│   ├── css/styles.css                 ← the only stylesheet you need
│   └── img/
│       ├── icon.png                   ← S monogram (transparent)
│       └── logo.png                   ← full Schreibly lockup
│
└── ftl/                               ← production Freemarker templates
    ├── template.ftl                   ← <@layout.registrationLayout> macro
    ├── login.ftl
    ├── register.ftl
    ├── login-reset-password.ftl
    ├── login-otp.ftl
    ├── error.ftl
    └── messages/
        ├── messages_en.properties     ← English overrides
        └── messages_de.properties     ← German overrides
```

## Installing into a Keycloak server

1. Copy this directory into Keycloak's `themes/` folder, naming it
   `schreibly`, so the final layout is:

   ```
   $KEYCLOAK_HOME/themes/schreibly/
       theme.properties
       login/
           template.ftl
           login.ftl
           register.ftl
           login-reset-password.ftl
           login-otp.ftl
           error.ftl
           messages/
               messages_en.properties
               messages_de.properties
           resources/
               css/styles.css
               img/icon.png
               img/logo.png
   ```

   To do this from this project, move the contents of `ftl/` into a `login/`
   directory and place `resources/` under it:

   ```bash
   mkdir -p themes/schreibly/login
   mv ftl/* themes/schreibly/login/
   mv resources themes/schreibly/login/
   mv theme.properties themes/schreibly/
   ```

2. Restart Keycloak (or, in dev: `bin/kc.sh start-dev`).

3. In the Keycloak Admin Console, open your realm → **Realm settings → Themes**
   and set **Login theme** to **schreibly**.

4. (Optional) Add additional locales to `theme.properties` (`locales=en,de,fr,ar`)
   and add the corresponding `messages_*.properties` files.

## Local preview

Open `login.html`, `register.html`, `forgot-password.html`, `otp.html`, or
`error.html` in a browser. The static previews use the same stylesheet, so
what you see is what Keycloak will render.

## Customising

All visual tokens live at the top of `resources/css/styles.css` under
`:root`. Adjust the brand colors, font stack, radii or shadows there and
every page picks the changes up immediately.

## License

Created for Schreibly. Reuse internally.
