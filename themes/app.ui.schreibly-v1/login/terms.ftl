<#import "template.ftl" as layout>
<@layout.registrationLayout displayMessage=true; section>
    <#if section = "header">
        ${msg("schrTermsTitle")}
    <#elseif section = "form">

    <#--
        Registration gate: accept the Terms of Service, acknowledge the Privacy Policy.

        The Privacy Policy is ACKNOWLEDGED, never consented to: the legal basis for the
        processing is Art. 6(1)(b) GDPR (performance of the contract), not consent.
        The data-collection / training consent is Art. 6(1)(a), is opt-in and separately
        withdrawable, and lives on the account as the `data-collection` role -- it must
        never be added to this screen (Art. 7(4) GDPR).

        Both boxes are `required`, so an unticked box is blocked by native HTML form
        validation. No JavaScript is involved. "Cancel" carries `formnovalidate` so it
        can still submit with the boxes untouched; the built-in TERMS_AND_CONDITIONS
        required action treats a `cancel` parameter as a decline.

        `kc_locale` is appended to the POST target on purpose: LoginActionsService turns
        it into the `locale_user_requested` auth note, and the `update_user_locale`
        required action then persists it as the user's `locale` attribute. That is what
        makes the recorded `terms_locale` provably the language this text was shown in.
    -->
        <#assign termsUrl = "https://schreibly.com/legal/terms">
        <#assign privacyUrl = "https://schreibly.com/legal/privacy">
        <#assign tosLink = '<a href="' + termsUrl + '" target="_blank" rel="noopener noreferrer">' + msg("schrTermsTosLink") + '</a>'>
        <#assign privacyLink = '<a href="' + privacyUrl + '" target="_blank" rel="noopener noreferrer">' + msg("schrTermsPrivacyLink") + '</a>'>
        <#assign termsAction = url.loginAction>
        <#if realm.internationalizationEnabled>
            <#assign termsAction = termsAction + "&kc_locale=" + locale.currentLanguageTag>
        </#if>

        <form id="kc-terms-form" action="${termsAction}" method="POST">

            <div id="kc-terms-checks">
                <div class="kc-terms-check">
                    <input type="checkbox" id="kc-terms-tos" name="schrTermsTos" value="on" required />
                    <label for="kc-terms-tos">${msg("schrTermsAcceptTos", tosLink)?no_esc}</label>
                </div>
                <div class="kc-terms-check">
                    <input type="checkbox" id="kc-terms-privacy" name="schrTermsPrivacy" value="on" required />
                    <label for="kc-terms-privacy">${msg("schrTermsAckPrivacy", privacyLink)?no_esc}</label>
                </div>
            </div>

            <div id="kc-terms-buttons">
                <input type="submit" name="accept" id="kc-accept"
                       class="${properties.kcButtonClass!} ${properties.kcButtonPrimaryClass!} ${properties.kcButtonLargeClass!}"
                       value="${msg("schrTermsDoAccept")}" />
                <input type="submit" name="cancel" id="kc-decline" formnovalidate
                       class="${properties.kcButtonClass!} ${properties.kcButtonDefaultClass!} ${properties.kcButtonLargeClass!}"
                       value="${msg("schrTermsDoCancel")}" />
            </div>
        </form>
    </#if>
</@layout.registrationLayout>
