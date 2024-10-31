package com.isitdtu.hihi;

import java.io.Serializable;

public class Users implements Serializable {
    private String name;
    private static final long serialVersionUID = 8107928321213067187L;
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
