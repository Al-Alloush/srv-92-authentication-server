<#import "template.ftl" as layout>
<#--
  Email-verification page shown right after registration (the VERIFY_EMAIL required action).
  Adds on top of the base template:
    * a reminder that the verification email may land in the spam / junk folder
    * a "back to main page" button
    * an auto-redirect to the main page with a visible seconds countdown
  Adjust countdownSeconds below to change the timer.
-->
<#assign countdownSeconds = 30>
<@layout.registrationLayout displayInfo=true; section>
    <#if section = "header">
        ${msg("emailVerifyTitle")}
    <#elseif section = "form">
        <#-- Application main page; fall back to the login page if the client has no base URL. -->
        <#assign mainPageUrl = (client.baseUrl)!''>
        <#if !mainPageUrl?has_content>
            <#assign mainPageUrl = url.loginUrl>
        </#if>

        <p class="instruction">${msg("emailVerifyInstruction1",user.email)}</p>

        <#-- The verification email can be filtered into spam / junk. -->
        <div id="kc-spam-notice" style="margin:18px 0 4px;padding:14px 16px;background:#eef6fb;border:1px solid #cfe6f3;border-radius:8px;font-size:14px;line-height:1.6;color:#1f3a5f;">
            ${msg("emailVerifySpamNotice")}
        </div>

        <#-- Back to the main page + auto-redirect countdown. -->
        <div id="kc-back-to-main" style="margin-top:24px;text-align:center;">
            <a href="${mainPageUrl}" id="kc-back-btn"
               style="display:inline-block;background:#0099d3;color:#ffffff;padding:12px 30px;border-radius:6px;text-decoration:none;font-size:15px;font-weight:600;">
                ${msg("backToMainPage")}
            </a>
            <p id="kc-redirect-note" style="margin:14px 0 0;font-size:13px;color:#6b7280;">
                ${msg("redirectCountdown",'<span id="kc-countdown">' + countdownSeconds + '</span>')?no_esc}
            </p>
        </div>

        <script>
            (function () {
                var seconds = ${countdownSeconds};
                var counter = document.getElementById("kc-countdown");
                var target  = "${mainPageUrl?js_string}";
                var ticker = setInterval(function () {
                    seconds -= 1;
                    if (counter) { counter.textContent = seconds; }
                    if (seconds <= 0) {
                        clearInterval(ticker);
                        window.location.href = target;
                    }
                }, 1000);
            })();
        </script>
    <#elseif section = "info">
        <p class="instruction">
            ${msg("emailVerifyInstruction2")}
            <br/>
            <a href="${url.loginAction}">${msg("doClickHere")}</a> ${msg("emailVerifyInstruction3")}
        </p>
    </#if>
</@layout.registrationLayout>
