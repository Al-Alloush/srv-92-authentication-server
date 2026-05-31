<#macro emailLayout>
<!DOCTYPE html>
<html lang="${(locale.currentLanguageTag)!'en'}" <#if (locale.rtl)!false>dir="rtl"</#if>>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <style type="text/css">
        body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
        table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
        img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
        @media only screen and (max-width: 620px) {
            .email-container { width: 100% !important; }
            .content-cell { padding: 28px 20px !important; }
            .header-cell { padding: 22px 20px !important; }
            .footer-cell { padding: 18px 20px !important; }
        }
    </style>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;width:100%;">

<!-- Hidden preheader -->
<div style="display:none;max-height:0;overflow:hidden;">Schreibly &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8;">
    <tr>
        <td align="center" style="padding:40px 16px;">

            <table role="presentation" class="email-container" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

                <#-- Header logo: the schreibly-logo.png asset from the app.ui.schreibly LOGIN
                     theme, served by Keycloak. The "/resources/<ver>/" segment is tied to the
                     Keycloak version — if Keycloak is upgraded, open the login page and refresh
                     <ver> with the new value (currently 26.5.3 -> lcdo4). -->
                <!-- Header -->
                <tr>
                    <td class="header-cell" align="center" style="background-color:#ffffff;border:1px solid #e2e8f0;border-bottom:none;border-radius:10px 10px 0 0;padding:32px 40px;text-align:center;">
                        <img src="https://auth.codexo.dev/resources/lcdo4/login/app.ui.schreibly/img/schreibly-logo.png"
                             alt="Schreibly" width="190" height="57"
                             style="display:block;margin:0 auto;width:190px;height:auto;max-width:70%;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;" />
                    </td>
                </tr>

                <!-- Accent line -->
                <tr>
                    <td style="height:4px;background-color:#0099d3;font-size:0;line-height:0;border-left:1px solid #e2e8f0;border-right:1px solid #e2e8f0;">&nbsp;</td>
                </tr>

                <!-- Body -->
                <tr>
                    <td class="content-cell" style="background-color:#ffffff;padding:40px;border-left:1px solid #e2e8f0;border-right:1px solid #e2e8f0;font-size:16px;line-height:1.7;color:#374151;">
                        <#nested>
                    </td>
                </tr>

                <!-- Footer -->
                <tr>
                    <td class="footer-cell" style="background-color:#f8fafc;border-radius:0 0 10px 10px;border:1px solid #e2e8f0;border-top:none;padding:24px 40px;text-align:center;">
                        <p style="margin:0 0 6px;color:#6b7280;font-size:13px;line-height:1.5;">
                            &copy; ${.now?string("yyyy")} Schreibly &mdash; Codexo
                        </p>
                        <p style="margin:0;color:#9ca3af;font-size:11px;line-height:1.5;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </td>
                </tr>

            </table>

        </td>
    </tr>
</table>

</body>
</html>
</#macro>
