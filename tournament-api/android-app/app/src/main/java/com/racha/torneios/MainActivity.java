package com.racha.torneios;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String PREFS = "racha";
    private static final String SERVER_URL = "server_url";
    private static final int INK = Color.rgb(23, 16, 32);
    private static final int ORANGE = Color.rgb(255, 173, 52);

    private FrameLayout root;
    private WebView webView;
    private View setupView;
    private EditText addressInput;
    private TextView helpText;
    private ProgressBar progress;
    private View fullscreenView;
    private WebChromeClient.CustomViewCallback fullscreenCallback;
    private String serverUrl = "";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(INK);
        getWindow().setNavigationBarColor(INK);

        root = new FrameLayout(this);
        root.setFitsSystemWindows(true);
        setContentView(root);

        webView = new WebView(this);
        webView.setBackgroundColor(INK);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setAllowFileAccess(false);
        webView.getSettings().setUserAgentString(webView.getSettings().getUserAgentString() + " RachaAndroid/1.0");
        webView.setWebViewClient(new RachaWebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onShowCustomView(View view, CustomViewCallback callback) {
                if (fullscreenView != null) {
                    callback.onCustomViewHidden();
                    return;
                }
                fullscreenView = view;
                fullscreenCallback = callback;
                webView.setVisibility(View.GONE);
                root.addView(view, new FrameLayout.LayoutParams(-1, -1));
                getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
            }

            @Override
            public void onHideCustomView() {
                hideFullscreen();
            }
        });
        root.addView(webView, new FrameLayout.LayoutParams(-1, -1));

        setupView = createSetupView();
        root.addView(setupView, new FrameLayout.LayoutParams(-1, -1));

        progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progress.setIndeterminate(true);
        FrameLayout.LayoutParams bar = new FrameLayout.LayoutParams(-1, dp(3), Gravity.TOP);
        root.addView(progress, bar);
        progress.setVisibility(View.GONE);

        String saved = getPreferences(MODE_PRIVATE).getString(SERVER_URL, "");
        if (saved.isEmpty()) {
            showSetup(null);
        } else {
            connect(saved);
        }
    }

    private View createSetupView() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(INK);
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setGravity(Gravity.CENTER_VERTICAL);
        column.setPadding(dp(28), dp(40), dp(28), dp(40));
        scroll.addView(column);

        TextView mark = text("R!", 76, ORANGE, true);
        column.addView(mark);
        TextView title = text("RACHA!", 46, Color.WHITE, true);
        column.addView(title);
        TextView subtitle = text("O jogo no seu bolso.", 20, Color.rgb(221, 191, 242), true);
        subtitle.setPadding(0, dp(6), 0, dp(28));
        column.addView(subtitle);

        TextView label = text("ENDEREÇO DA API NO PC", 12, ORANGE, true);
        column.addView(label);
        addressInput = new EditText(this);
        addressInput.setSingleLine(true);
        addressInput.setInputType(android.text.InputType.TYPE_TEXT_VARIATION_URI);
        addressInput.setHint("http://192.168.1.10:8000");
        addressInput.setTextColor(INK);
        addressInput.setHintTextColor(Color.GRAY);
        addressInput.setPadding(dp(14), 0, dp(14), 0);
        GradientDrawable field = new GradientDrawable();
        field.setColor(Color.WHITE);
        field.setCornerRadius(dp(10));
        addressInput.setBackground(field);
        LinearLayout.LayoutParams inputParams = new LinearLayout.LayoutParams(-1, dp(54));
        inputParams.topMargin = dp(10);
        column.addView(addressInput, inputParams);

        Button connectButton = new Button(this);
        connectButton.setText("CONECTAR À QUADRA  ↗");
        connectButton.setAllCaps(false);
        connectButton.setTextColor(INK);
        connectButton.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        GradientDrawable buttonBackground = new GradientDrawable();
        buttonBackground.setColor(ORANGE);
        buttonBackground.setCornerRadius(dp(10));
        connectButton.setBackground(buttonBackground);
        LinearLayout.LayoutParams buttonParams = new LinearLayout.LayoutParams(-1, dp(54));
        buttonParams.topMargin = dp(14);
        column.addView(connectButton, buttonParams);
        connectButton.setOnClickListener(view -> {
            String value = normalizeAddress(addressInput.getText().toString());
            if (value == null) {
                helpText.setText("Digite um endereço válido, como http://192.168.1.10:8000");
                return;
            }
            connect(value);
        });

        helpText = text("Deixe a API ligada no PC e conecte os dois aparelhos ao mesmo Wi-Fi.", 14, Color.rgb(201, 186, 209), false);
        helpText.setPadding(0, dp(18), 0, 0);
        column.addView(helpText);
        return scroll;
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return view;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private String normalizeAddress(String input) {
        String value = input.trim();
        if (value.isEmpty()) return null;
        if (!value.contains("://")) value = "http://" + value;
        Uri uri = Uri.parse(value);
        if (!("http".equals(uri.getScheme()) || "https".equals(uri.getScheme())) || uri.getHost() == null) return null;
        return uri.getScheme() + "://" + uri.getAuthority() + "/";
    }

    private void connect(String url) {
        serverUrl = url;
        addressInput.setText(url);
        getPreferences(MODE_PRIVATE).edit().putString(SERVER_URL, url).apply();
        setupView.setVisibility(View.GONE);
        webView.setVisibility(View.VISIBLE);
        progress.setVisibility(View.VISIBLE);
        webView.loadUrl(url);
    }

    private void showSetup(String error) {
        progress.setVisibility(View.GONE);
        webView.setVisibility(View.GONE);
        setupView.setVisibility(View.VISIBLE);
        if (error != null) helpText.setText(error);
        else helpText.setText("Deixe a API ligada no PC e conecte os dois aparelhos ao mesmo Wi-Fi.");
        if (!serverUrl.isEmpty()) addressInput.setText(serverUrl);
    }

    private void hideFullscreen() {
        if (fullscreenView == null) return;
        root.removeView(fullscreenView);
        fullscreenView = null;
        webView.setVisibility(View.VISIBLE);
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        if (fullscreenCallback != null) fullscreenCallback.onCustomViewHidden();
        fullscreenCallback = null;
    }

    private class RachaWebViewClient extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            if ("racha".equals(uri.getScheme())) {
                showSetup(null);
                return true;
            }
            Uri server = Uri.parse(serverUrl);
            if (("http".equals(uri.getScheme()) || "https".equals(uri.getScheme())) && !server.getHost().equals(uri.getHost())) {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
                return true;
            }
            return false;
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            progress.setVisibility(View.GONE);
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (request.isForMainFrame()) showSetup("Não foi possível conectar. Confira o IP do PC, o Wi-Fi e se a API está ligada.");
        }
    }

    @Override
    public void onBackPressed() {
        if (fullscreenView != null) {
            hideFullscreen();
            return;
        }
        if (setupView.getVisibility() == View.VISIBLE) {
            super.onBackPressed();
            return;
        }
        webView.evaluateJavascript("(function(){var s=document.getElementById('score-screen');if(s&&!s.hidden){document.getElementById('close-score').click();return true}return false})()", result -> {
            if ("true".equals(result)) return;
            if (webView.canGoBack()) webView.goBack();
            else MainActivity.super.onBackPressed();
        });
    }

    @Override
    protected void onDestroy() {
        if (webView != null) webView.destroy();
        super.onDestroy();
    }
}
