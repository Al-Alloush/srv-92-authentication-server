<#ftl output_format="plainText">
${msg("emailUpdateConfirmationBody", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), newEmail, "Schreibly", linkExpirationFormatter(linkExpiration))}
