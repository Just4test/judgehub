import java.io.File;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.net.*;
import java.util.Iterator;
import java.util.Vector;

class SolutionLoader {

    public static void listLoadedClasses(ClassLoader byClassLoader) {
        Class clKlass = byClassLoader.getClass();
        System.out.println("Classloader: " + clKlass.getCanonicalName());
        while (clKlass != java.lang.ClassLoader.class) {
            clKlass = clKlass.getSuperclass();
        }
        try {
            java.lang.reflect.Field fldClasses = clKlass
                    .getDeclaredField("classes");
            fldClasses.setAccessible(true);
            Vector classes = (Vector) fldClasses.get(byClassLoader);
            for (Iterator iter = classes.iterator(); iter.hasNext();) {
                System.out.println("   Loaded " + iter.next());
            }
        } catch (SecurityException e) {
            e.printStackTrace();
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        } catch (NoSuchFieldException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        File file = new File("/Users/just4test/Documents/SideProject/onlinejudge/");

        URL url = null;
        try {
            url = file.toURI().toURL();
            System.out.println(url);

        } catch (MalformedURLException e) {
            System.err.println(".class file doesn't exists.");
            e.printStackTrace();
            return;
        }
        URL[] urls = new URL[]{url};
        URLClassLoader loader = new URLClassLoader(urls);

        listLoadedClasses(loader);

        try {
            Class Solution = loader.loadClass("Solution");
//            Constructor<?> constructor = Solution.getConstructor();
//            constructor.setAccessible(true);
//            constructor.setAccessible(true);

            Constructor[] constructors = Solution.getDeclaredConstructors();
            constructors[0].setAccessible(true);
            constructors[0].newInstance();
//            for (Constructor<?> c :constructors) {
//                c.setAccessible(true);
//
//            }
            

            Object solution = constructors[0].newInstance();
//            Method[] methods=Solution.getDeclaredMethods();

            Class[] parameterTypes = new Class[2];
            parameterTypes[0] = int[].class;
            parameterTypes[1] = int.class;
            Method method = Solution.getDeclaredMethod("twoSum", parameterTypes);
            method.setAccessible(true);
            Object result = method.invoke(solution, null, 1);
            System.out.println(result.toString());

        } catch (ClassNotFoundException e) {
            System.err.println("There are no Solution class.");
            e.printStackTrace();
            return;
        } catch (InstantiationException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        }

    }
}