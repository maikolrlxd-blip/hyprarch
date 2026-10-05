# El puente de anuncios se invoca por nombre desde JavaScript: no debe ofuscarse ni eliminarse.
-keepclassmembers class com.hyprarch.game.MainActivity$AdsBridge {
    @android.webkit.JavascriptInterface <methods>;
}
-keepclassmembers class com.hyprarch.game.MainActivity$NativeBridge {
    @android.webkit.JavascriptInterface <methods>;
}
