<#import "template.ftl" as layout>
<@layout.registrationLayout displayMessage=!messagesPerField.existsError('username'); section>

<#if section = "header">
  <h1 class="kc-title">${msg("emailForgotTitle")}</h1>
  <p class="kc-subtitle">${msg("emailInstruction")!"We'll email you a secure link to set a new password."}</p>

<#elseif section = "form">
  <form class="kc-form" action="${url.loginAction}" method="post">
    <div class="kc-field">
      <label class="kc-label" for="username">
        <#if !realm.loginWithEmailAllowed>${msg("username")}
        <#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}
        <#else>${msg("email")}</#if>
      </label>
      <input class="kc-input <#if messagesPerField.existsError('username')>kc-input--invalid</#if>"
             id="username" name="username" type="text" autofocus
             value="${(auth.attemptedUsername!'')}" autocomplete="email" />
    </div>
    <button class="kc-btn kc-btn--primary" type="submit">${msg("doSubmit")}</button>
  </form>

<#elseif section = "info">
  <p class="kc-foot"><a class="kc-link" href="${url.loginUrl}">${msg("backToLogin")}</a></p>
</#if>

</@layout.registrationLayout>
