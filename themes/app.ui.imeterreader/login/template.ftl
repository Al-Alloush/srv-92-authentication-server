<#import "footer.ftl" as loginFooter>
<#macro registrationLayout bodyClass="" displayInfo=false displayMessage=true displayRequiredFields=false>
<!DOCTYPE html>
<html class="${properties.kcHtmlClass!}"<#if realm.internationalizationEnabled> lang="${locale.currentLanguageTag}" dir="${(locale.rtl)?then('rtl','ltr')}"</#if>>

<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="robots" content="noindex, nofollow">

    <#if properties.meta?has_content>
        <#list properties.meta?split(' ') as meta>
            <meta name="${meta?split('==')[0]}" content="${meta?split('==')[1]}"/>
        </#list>
    </#if>
    <title>${msg("loginTitle",(realm.displayName!''))}</title>
    <link rel="icon" href="${url.resourcesPath}/img/favicon.ico" />
    <#if properties.stylesCommon?has_content>
        <#list properties.stylesCommon?split(' ') as style>
            <link href="${url.resourcesCommonPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <#if properties.styles?has_content>
        <#list properties.styles?split(' ') as style>
            <link href="${url.resourcesPath}/${style}" rel="stylesheet" />
        </#list>
    </#if>
    <#if properties.scripts?has_content>
        <#list properties.scripts?split(' ') as script>
            <script src="${url.resourcesPath}/${script}" type="text/javascript"></script>
        </#list>
    </#if>
    <script type="importmap">
        {
            "imports": {
                "rfc4648": "${url.resourcesCommonPath}/vendor/rfc4648/rfc4648.js"
            }
        }
    </script>
    <script src="${url.resourcesPath}/js/menu-button-links.js" type="module"></script>
    <#if scripts??>
        <#list scripts as script>
            <script src="${script}" type="text/javascript"></script>
        </#list>
    </#if>
    <script type="module">
        import { checkCookiesAndSetTimer } from "${url.resourcesPath}/js/authChecker.js";

        checkCookiesAndSetTimer(
          "${url.ssoLoginInOtherTabsUrl?no_esc}"
        );
    </script>
    <style>
        #kc-app-name{font-size:14px!important;font-weight:600!important;color:#6b7280!important;text-align:center;margin-top:8px;}
        .login-pf-page .card-pf.has-auth-tabs{padding-left:0!important;padding-right:0!important;}
        .login-pf-page .has-auth-tabs .login-pf-header{padding:0 20px;margin-bottom:0!important;}
        .has-auth-tabs #kc-content{padding:0 20px;}
        @media(min-width:768px){
            .login-pf-page .has-auth-tabs .login-pf-header{padding:0 40px;}
            .has-auth-tabs #kc-content{padding:0 40px;}
        }
        #kc-auth-tabs{display:flex;width:100%;border-bottom:3px solid #e8edf2;background:#f7f9fb;}
        .kc-auth-tab{flex:1;padding:18px 8px;background:transparent;border:none;border-bottom:3px solid transparent;margin-bottom:-3px;cursor:pointer;font-size:16px;font-weight:500;color:#6b7280;text-align:center;font-family:inherit;}
        .kc-auth-tab.active{color:#0099d3;border-bottom-color:#0099d3;font-weight:700;background:#fff;}
        .kc-auth-tab:not(.active):hover{color:#374151;background:#eef2f6;}
        .has-auth-tabs #kc-info{display:none;}
        .has-auth-tabs #kc-content-wrapper{margin-top:24px;}
        .login-pf body{min-height:100%!important;height:auto!important;overflow-y:auto!important;}
        .login-pf-page{padding-bottom:30px;}
    </style>
</head>

<body class="${properties.kcBodyClass!}">
<div class="${properties.kcLoginClass!}">
    <div id="kc-header" class="${properties.kcHeaderClass!}">
        <div id="kc-header-wrapper" class="${properties.kcHeaderWrapperClass!}"></div>
    </div>

    <#assign isRegisterPage = !login?? && (profile?? || register??)>
    <#assign showTabs = (login?? || isRegisterPage) && realm.registrationAllowed>

    <div class="${properties.kcFormCardClass!}<#if showTabs> has-auth-tabs</#if>">
        <header class="${properties.kcFormHeaderClass!}">

            <#-- Language switcher -->
            <#if realm.internationalizationEnabled && locale.supported?size gt 1>
                <div class="${properties.kcLocaleMainClass!}" id="kc-locale">
                    <div id="kc-locale-wrapper" class="${properties.kcLocaleWrapperClass!}">
                        <div id="kc-locale-dropdown" class="menu-button-links ${properties.kcLocaleDropDownClass!}">
                            <button tabindex="1" id="kc-current-locale-link" aria-label="${msg("languages")}" aria-haspopup="true" aria-expanded="false" aria-controls="language-switch1">${locale.current}</button>
                            <ul role="menu" tabindex="-1" aria-labelledby="kc-current-locale-link" aria-activedescendant="" id="language-switch1" class="${properties.kcLocaleListClass!}">
                                <#assign i = 1>
                                <#list locale.supported as l>
                                    <li class="${properties.kcLocaleListItemClass!}" role="none">
                                        <a role="menuitem" id="language-${i}" class="${properties.kcLocaleItemClass!}" href="${l.url}">${l.label}</a>
                                    </li>
                                    <#assign i++>
                                </#list>
                            </ul>
                        </div>
                    </div>
                </div>
            </#if>

            <#-- Logo and app name -->
            <div id="kc-logo-wrapper">
                <img src="${url.resourcesPath}/img/imeterrecorder-logo.png" alt="${realm.displayName!''}" id="kc-logo-img" />
                <div id="kc-app-name">
                    <#if locale.currentLanguageTag == "ar">قارئ العدادات الذكي<#else>iMeterReader</#if>
                </div>
            </div>

            <#-- Page title: shown only on non-tab pages (OTP, forgot password, etc.) -->
            <#if auth?has_content && auth.showUsername() && !auth.showResetCredentials()>
                <#if displayRequiredFields>
                    <div class="${properties.kcContentWrapperClass!}">
                        <div class="${properties.kcLabelWrapperClass!} subtitle">
                            <span class="subtitle"><span class="required">*</span> ${msg("requiredFields")}</span>
                        </div>
                        <div class="col-md-10">
                            <#nested "show-username">
                            <div id="kc-username" class="${properties.kcFormGroupClass!}">
                                <label id="kc-attempted-username">${auth.attemptedUsername}</label>
                                <a id="reset-login" href="${url.loginRestartFlowUrl}" aria-label="${msg("restartLoginTooltip")}">
                                    <div class="kc-login-tooltip">
                                        <i class="${properties.kcResetFlowIcon!}"></i>
                                        <span class="kc-tooltip-text">${msg("restartLoginTooltip")}</span>
                                    </div>
                                </a>
                            </div>
                        </div>
                    </div>
                <#else>
                    <#nested "show-username">
                    <div id="kc-username" class="${properties.kcFormGroupClass!}">
                        <label id="kc-attempted-username">${auth.attemptedUsername}</label>
                        <a id="reset-login" href="${url.loginRestartFlowUrl}" aria-label="${msg("restartLoginTooltip")}">
                            <div class="kc-login-tooltip">
                                <i class="${properties.kcResetFlowIcon!}"></i>
                                <span class="kc-tooltip-text">${msg("restartLoginTooltip")}</span>
                            </div>
                        </a>
                    </div>
                </#if>
            <#elseif !showTabs>
                <#if displayRequiredFields>
                    <div class="${properties.kcContentWrapperClass!}">
                        <div class="${properties.kcLabelWrapperClass!} subtitle">
                            <span class="subtitle"><span class="required">*</span> ${msg("requiredFields")}</span>
                        </div>
                        <div class="col-md-10">
                            <h1 id="kc-page-title"><#nested "header"></h1>
                        </div>
                    </div>
                <#else>
                    <h1 id="kc-page-title"><#nested "header"></h1>
                </#if>
            </#if>

        </header>

        <#-- Auth tabs: direct child of card so margin: 0 -20px gives full width -->
        <#if showTabs>
        <div id="kc-auth-tabs">
            <button class="kc-auth-tab" id="tab-login"
                onclick="location.href='${url.loginUrl?no_esc}'">
                ${msg("doLogIn")}
            </button>
            <button class="kc-auth-tab" id="tab-register"
                onclick="location.href='${url.registrationUrl?no_esc}'">
                ${msg("doRegister")}
            </button>
        </div>
        <script>
        (function() {
            var isRegister = window.location.pathname.indexOf('registration') !== -1;
            var t = document.getElementById(isRegister ? 'tab-register' : 'tab-login');
            if (t) t.classList.add('active');
        })();
        </script>
        </#if>

        <div id="kc-content">
            <div id="kc-content-wrapper">

                <#if displayMessage && message?has_content && (message.type != 'warning' || !isAppInitiatedAction??)>
                    <div class="alert-${message.type} ${properties.kcAlertClass!} pf-m-<#if message.type = 'error'>danger<#else>${message.type}</#if>">
                        <div class="pf-c-alert__icon">
                            <#if message.type = 'success'><span class="${properties.kcFeedbackSuccessIcon!}"></span></#if>
                            <#if message.type = 'warning'><span class="${properties.kcFeedbackWarningIcon!}"></span></#if>
                            <#if message.type = 'error'><span class="${properties.kcFeedbackErrorIcon!}"></span></#if>
                            <#if message.type = 'info'><span class="${properties.kcFeedbackInfoIcon!}"></span></#if>
                        </div>
                        <span class="${properties.kcAlertTitleClass!}">${kcSanitize(message.summary)?no_esc}</span>
                    </div>
                </#if>

                <#nested "form">

                <#if auth?has_content && auth.showTryAnotherWayLink()>
                    <form id="kc-select-try-another-way-form" action="${url.loginAction}" method="post">
                        <div class="${properties.kcFormGroupClass!}">
                            <input type="hidden" name="tryAnotherWay" value="on"/>
                            <a href="#" id="try-another-way"
                               onclick="document.forms['kc-select-try-another-way-form'].submit();return false;">${msg("doTryAnotherWay")}</a>
                        </div>
                    </form>
                </#if>

                <#nested "socialProviders">

                <#if displayInfo>
                    <div id="kc-info" class="${properties.kcSignUpClass!}">
                        <div id="kc-info-wrapper" class="${properties.kcInfoAreaWrapperClass!}">
                            <#nested "info">
                        </div>
                    </div>
                </#if>
            </div>
        </div>

        <@loginFooter.content/>
    </div>
</div>
</body>
</html>
</#macro>
