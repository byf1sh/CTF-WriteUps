package com.isitdtu.hihi.Helpers;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

import com.isitdtu.hihi.Users;
public class SecureObjectInputStream extends ObjectInputStream {
    public SecureObjectInputStream(ByteArrayInputStream inputStream) throws IOException {
        super(inputStream);
    }

    @Override
    protected Class<?> resolveClass(ObjectStreamClass osc) throws IOException ,ClassNotFoundException{
        List<String> approvedClass = new ArrayList<String>();
        approvedClass.add(Users.class.getName());

        if(!approvedClass.contains(osc.getName())){
            throw new InvalidClassException("Can not deserialize this class! ",osc.getName());
        }
        return super.resolveClass(osc);
    }
}
