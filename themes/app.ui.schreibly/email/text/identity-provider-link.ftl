<#ftl output_format="plainText">
${msg("identityProviderLinkBody", identityProviderDisplayName, "Schreibly", identityProviderContext.username, link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, linkExpirationFormatter(linkExpiration))}
