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
