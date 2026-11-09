<#ftl output_format="plainText">
${msg("passwordResetBody", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, "Schreibly", linkExpirationFormatter(linkExpiration))}
