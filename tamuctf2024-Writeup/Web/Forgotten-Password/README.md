# Forgotten Password - Web - tamuctf-2024

Pada challenge kali ini terdapat kerentanan pada fitur forgot password, yang mana kita bisa memanipulasi field send email, kita bisa mengirimkan request forgot password ke domain kita dan mendapatkan password baru

## Source Code
```ruby
class AuthController < ApplicationController
  def login
  end

  def forget
  end

  def recover
    user_found = false
    User.all.each { |user|
      if params[:email].include?(user.email)
        user_found = true
        break
      end
    }

    if user_found
      RecoveryMailer.recovery_email(params[:email]).deliver_now
      redirect_to forgot_password_path, notice: 'Password reset email sent'
    else
      redirect_to forgot_password_path, alert: 'You are not a registered user!'
    end

  end
end
```

karena pemeriksaan user dilakukan dengan `params[:email]`, kita bisa memasukan injeksi seperti `b8500763@gmail.com,<your-email>@gmail.com`, dan sistem akan mengirimkan password baru ke domain kita. dan password tersebut berisi flag.