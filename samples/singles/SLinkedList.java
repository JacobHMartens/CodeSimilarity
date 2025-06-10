import java.lang.*;
import java.util.*;
import java.io.*;

class SLinkedList {
    private int data;
    private SLinkedList next;

    public SLinkedList() {
        data = 0;
        next = null;
    }

    public SLinkedList(int value) {
        data = value;
        next = null;
    }

    public SLinkedList InsertNext(int value) {
        SLinkedList node = new SLinkedList(value);
        if (this.next == null) {
            // Easy to handle
            node.next = null; // already set in constructor
            this.next = node;
        } else {
            // Insert in the middle
            SLinkedList temp = this.next;
            node.next = temp;
            this.next = node;
        }
        return node;
    }

    public int DeleteNext() {
        if (next == null)
            return 0;

        SLinkedList node = this.next;
        this.next = this.next.next; // can be NULL here
        node = null;
        return 1;
    }

    public void Traverse(SLinkedList node) {
        if (node == null)
            node = this;
        System.out.println("\n\nTraversing in Forward Direction\n\n");

        while (node != null) {
            System.out.println(node.data);
            node = node.next;
        }
    }

    public static void main(String[] args) {
        SLinkedList node1 = new SLinkedList(1);
        SLinkedList node2 = node1.InsertNext(2);
        SLinkedList node3 = node2.InsertNext(3);
        SLinkedList node4 = node3.InsertNext(4);
        SLinkedList node5 = node4.InsertNext(5);

        node1.Traverse(null);
        node3.DeleteNext(); // delete the node "4"
        node2.Traverse(null);

    }
}